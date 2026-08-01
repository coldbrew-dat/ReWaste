"""
admin_routes.py
a basic panel only an admin account can open
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from models.db import db
from models.models import User, Listing, Request

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('admin access only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    # shows overall platform numbers on one simple page
    total_users = User.query.count()
    total_listings = Listing.query.count()
    total_completed = Request.query.filter_by(status='completed').count()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_listings=total_listings,
        total_completed=total_completed,
    )


@admin_bp.route('/admin/businesses')
@admin_required
def admin_businesses():
    # shows every registered business
    all_users = User.query.all()
    return render_template('admin_businesses.html', all_users=all_users)


@admin_bp.route('/admin/listings')
@admin_required
def admin_listings():
    # shows every listing so the admin can spot bad or fake ones
    all_listings = Listing.query.all()
    return render_template('admin_listings.html', all_listings=all_listings)


@admin_bp.route('/admin/listings/<int:listing_id>/remove', methods=['POST'])
@admin_required
def admin_remove_listing(listing_id):
    # deletes one listing from the database
    listing = Listing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    flash('listing removed.', 'success')
    return redirect(url_for('admin.admin_listings'))


@admin_bp.route('/admin/businesses/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    # lets an admin edit any business's profile info
    target_user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        target_user.business_name = request.form.get('business_name', target_user.business_name).strip()
        target_user.email = request.form.get('email', target_user.email).strip()
        target_user.sector = request.form.get('sector', target_user.sector)
        target_user.city = request.form.get('city', target_user.city)
        target_user.is_admin = True if request.form.get('is_admin') == 'on' else False

        new_password = request.form.get('new_password', '').strip()
        if new_password:
            target_user.set_password(new_password)

        db.session.commit()
        flash('business updated.', 'success')
        return redirect(url_for('admin.admin_businesses'))

    return render_template('admin_edit_user.html', target_user=target_user)


@admin_bp.route('/admin/businesses/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    # removes a business entirely, along with everything tied to it
    target_user = User.query.get_or_404(user_id)

    if target_user.id == session.get('user_id'):
        flash('you cannot delete your own admin account while logged in.', 'error')
        return redirect(url_for('admin.admin_businesses'))

    # remove requests where this user was buyer or seller
    Request.query.filter(
        (Request.buyer_id == target_user.id) | (Request.seller_id == target_user.id)
    ).delete(synchronize_session=False)

    # remove their listings (this also removes any requests tied to those listings
    # via the cascade already set up on Listing.requests)
    for listing in Listing.query.filter_by(user_id=target_user.id).all():
        if listing.photo:
            import os
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], listing.photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
        db.session.delete(listing)

    if target_user.score:
        db.session.delete(target_user.score)

    db.session.delete(target_user)
    db.session.commit()
    flash('business and all associated data removed.', 'success')
    return redirect(url_for('admin.admin_businesses'))
