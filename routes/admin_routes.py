"""
admin_routes.py — haadiya's module
a basic panel only an admin account can open
"""
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from models.db import db
from models.models import User, Listing, Request
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MATERIAL_TYPES = ['Plastic', 'Metal', 'Paper', 'Fabric', 'Glass',
                  'Wood', 'Electronics', 'Rubber', 'Chemical', 'Other']
CITIES = ['Islamabad', 'Karachi', 'Lahore', 'Rawalpindi', 'Peshawar',
          'Quetta', 'Faisalabad', 'Multan', 'Hyderabad', 'Other']
UNITS = ['kg', 'tonnes', 'pieces', 'litres', 'meters']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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


@admin_bp.route('/admin/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_listing(listing_id):
    # lets the admin edit ANY listing, including uploading a photo,
    # without needing to own it
    listing = Listing.query.get_or_404(listing_id)

    if request.method == 'POST':
        listing.title         = request.form.get('title', listing.title).strip()
        listing.material_type = request.form.get('material_type', listing.material_type)
        listing.unit           = request.form.get('unit', listing.unit)
        listing.city          = request.form.get('city', listing.city)
        listing.description   = request.form.get('description', listing.description).strip()

        try:
            listing.quantity = float(request.form.get('quantity', listing.quantity))
        except ValueError:
            flash('Quantity must be a number.', 'error')
            return redirect(url_for('admin.admin_edit_listing', listing_id=listing_id))

        try:
            listing.price = float(request.form.get('price', listing.price))
        except ValueError:
            flash('Price must be a number.', 'error')
            return redirect(url_for('admin.admin_edit_listing', listing_id=listing_id))

        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            if listing.photo:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], listing.photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename    = secure_filename(photo_file.filename)
            unique_name = f"admin_{int(__import__('time').time())}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            photo_file.save(upload_path)
            listing.photo = unique_name

        db.session.commit()
        flash('Listing updated by admin.', 'success')
        return redirect(url_for('admin.admin_listings'))

    return render_template('edit_listing.html',
                           listing=listing,
                           material_types=MATERIAL_TYPES,
                           cities=CITIES,
                           units=UNITS)
