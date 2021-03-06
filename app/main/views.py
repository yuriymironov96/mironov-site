from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, current_app, \
    request, abort, flash, make_response
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, \
    PostForm, CommentForm, TagForm
from .. import db
from ..models import User, Role, Permission, Post, Comment, Tag, \
    Tag_Post_Relate
from ..email import send_email
from flask.ext.login import login_required, current_user
from ..decorators import admin_required, permission_required

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
        form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data,
            author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        for tag in form.tags.data:
            post.tagify(Tag.query.filter_by(id=tag).first())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(page,
        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
        pagination=pagination)


@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
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
        flash('The profile has been updated')
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
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        send_email(current_app.config['ADMIN'], 'User has commented on your post!', 'auth/email/notify_comment', user=current_user._get_current_object(), comment=comment, post=post)
        flash('Your comment has been published')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
                current_app.config['COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                            comments=comments, pagination=pagination,
                            post_title=post.title, single_post=True)

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/delete/<int:id>')
@admin_required
def delete(id):
    Post.query.filter_by(id=id).delete()
    flash("The post has been deleted")
    return redirect(url_for('main.index'))


@main.route('/tag/add', methods=['GET', 'POST'])
@admin_required
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        t = Tag(name=form.title.data)
        db.session.add(t)
        return redirect(url_for('.tag_add'))
    return render_template('add_tag.html', form=form)


@main.route('/tag/<int:id>')
def tag_search(id):
    tag = Tag.query.filter_by(id=id).first()
    if tag is None:
        flash('Invalid tag.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = tag.posts.paginate(page,
        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = [item.Post for item in pagination.items]
    return render_template('view_tag_res.html', tag=tag, posts=posts,
        pagination=pagination)

@main.route('/moderate/disable/<int:pid>/<int:cid>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(pid, cid):
    Comment.query.filter_by(id=cid).delete()
    flash('The comment has been deleted', category='message')
    return redirect(url_for('.post', id=pid))

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
