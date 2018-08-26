# -*- coding:utf-8 -*-
from . import main
from flask import render_template, abort, flash, redirect, url_for, request, current_app
from ..models import User, Role, Permission, Post, Comment
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, PostForm1
from .. import db, mysql
from ..decorators import admin_required, permission_required


@main.route('/mysqltest')
def mysqltest():
    cur = mysql.connection.cursor()
    cur.execute('show databases')
    rv = cur.fetchall()
    return render_template('mysqltest.html', rv=rv)


@main.route('/test', methods=['GET', 'POST'])
def test():
    form = PostForm()
    return render_template('test.html', form=form)


@main.route('/display-test', methods=['GET'])
def display_test():
    return '哈哈哈，怕了吧'


@main.route('/about-me')
def about_me():
    return render_template('about_me.html')


@main.route('/about-blog')
def about_blog():
    return render_template('about_blog.html')


@main.route('/mdtest')
def test1():
    mkd = '''
    # header
    ## header2
    [picture](https://goss.veer.com/creative/vcg/veer/1600water/veer-169767357.jpg)
    * 1
    * 2
    * 3
    **bold**
    '''

    return render_template('test1.html', mkd=mkd)


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=10, error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination,
                           display_full=False)


@main.route('/get_base')
def get_base():
    cur = mysql.connection.cursor()
    cur.execute("select date_format(timestamp, '%Y%m'), id from posts order by date_format(timestamp,'%Y%m') desc")
    rv = cur.fetchall()
    rv_dict = {}
    for v in rv:
        if v[0] not in rv_dict.keys():
            rv_dict[v[0]] = [v[1]]
        else:
            rv_dict[v[0]].append(v[1])
    print '----------------------'
    print rv_dict
    print '----------------------'
    cur.close()


@main.route('/addblog', methods=['POST', 'GET'])
def addblog():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.addblog'))

    return render_template('addblog.html', form=form, add=True)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your Profile has been updated')
        return redirect(url_for('.user', username=current_user.username))

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('comment has been published')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / int(current_app.config['FLASKY_COMMENTS_PER_PAGE']) + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=int(current_app.config['FLASKY_COMMENTS_PER_PAGE']), error_out=False
    )
#     pagination = post.comments.order_by(Comment.timestamp.asc())
    comments = pagination.items
    return render_template('post.html', posts=[post], comments=comments, form=form,
                           pagination=pagination, display_full=True)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.WRITE_ARTICLES):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.addblog', id=post.id))
    form.body.data = post.body
    return render_template('addblog.html', form=form, head='modify', id=id)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=int(current_app.config['FLASKY_COMMENTS_PER_PAGE']),
        error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@login_required
@main.route('/editmd/<int:id>', methods=['GET', 'POST'])
def editmd(id):
    pass
