"""
listing_routes.py
Handles: browse listings, create listing, view single listing,
         edit listing, delete listing, search + filter.
"""
import os
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, current_app)
from werkzeug.utils import secure_filename
from models.db import db
from models.models import Listing, User

listing_bp = Blueprint('listing', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MATERIAL_TYPES = ['Plastic', 'Metal', 'Paper', 'Fabric', 'Glass',
                  'Wood', 'Electronics', 'Rubber', 'Chemical', 'Other']
CITIES = ['Islamabad', 'Karachi', 'Lahore', 'Rawalpindi', 'Peshawar',
          'Quetta', 'Faisalabad', 'Multan', 'Hyderabad', 'Other']
UNITS = ['kg', 'tonnes', 'pieces', 'litres', 'meters']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Simple decorator — redirect to login if no session."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ── Home → redirect to browse ──────────────────────────────────────────────────
@listing_bp.route('/')
def index():
    return redirect(url_for('listing.browse'))


# ── Browse all listings (with search + filter) ─────────────────────────────────
@listing_bp.route('/listings')
def browse():
    query         = request.args.get('q', '').strip()
    material_type = request.args.get('material_type', '')
    city          = request.args.get('city', '')
    min_price     = request.args.get('min_price', '')
    max_price     = request.args.get('max_price', '')
    sort_by       = request.args.get('sort_by', 'newest')

    listings_q = Listing.query.filter_by(status='available')

    # Keyword search on title and description
    if query:
        listings_q = listings_q.filter(
            db.or_(
                Listing.title.ilike(f'%{query}%'),
                Listing.description.ilike(f'%{query}%')
            )
        )

    if material_type:
        listings_q = listings_q.filter_by(material_type=material_type)

    if city:
        listings_q = listings_q.filter_by(city=city)

    if min_price:
        try:
            listings_q = listings_q.filter(Listing.price >= float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            listings_q = listings_q.filter(Listing.price <= float(max_price))
        except ValueError:
            pass

    if sort_by == 'price_asc':
        listings_q = listings_q.order_by(Listing.price.asc())
    elif sort_by == 'price_desc':
        listings_q = listings_q.order_by(Listing.price.desc())
    else:
        listings_q = listings_q.order_by(Listing.created_at.desc())

    listings = listings_q.all()

    return render_template('browse.html',
                           listings=listings,
                           material_types=MATERIAL_TYPES,
                           cities=CITIES,
                           query=query,
                           selected_material=material_type,
                           selected_city=city,
                           min_price=min_price,
                           max_price=max_price,
                           sort_by=sort_by)


# ── Single listing detail ──────────────────────────────────────────────────────
@listing_bp.route('/listings/<int:listing_id>')
def view_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('view_listing.html', listing=listing)


# ── Create listing ─────────────────────────────────────────────────────────────
@listing_bp.route('/listings/new', methods=['GET', 'POST'])
@login_required
def create_listing():
    if request.method == 'POST':
        title         = request.form.get('title', '').strip()
        material_type = request.form.get('material_type', '').strip()
        quantity      = request.form.get('quantity', '').strip()
        unit          = request.form.get('unit', '').strip()
        price         = request.form.get('price', '').strip()
        description   = request.form.get('description', '').strip()
        city          = request.form.get('city', '').strip()
        photo_file    = request.files.get('photo')

        # Basic validation
        errors = []
        if not title:         errors.append('Title is required.')
        if not material_type: errors.append('Material type is required.')
        if not quantity:      errors.append('Quantity is required.')
        if not unit:          errors.append('Unit is required.')
        if not price:         errors.append('Price is required.')
        if not city:          errors.append('City is required.')

        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            errors.append('Quantity must be a number.')

        try:
            price = float(price)
        except (ValueError, TypeError):
            errors.append('Price must be a number.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('create_listing.html',
                                   material_types=MATERIAL_TYPES,
                                   cities=CITIES,
                                   units=UNITS)

        # Handle photo upload
        photo_filename = None
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            # Make filename unique
            unique_name = f"{session['user_id']}_{int(__import__('time').time())}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            photo_file.save(upload_path)
            photo_filename = unique_name

        new_listing = Listing(
            user_id=session['user_id'],
            title=title,
            material_type=material_type,
            quantity=quantity,
            unit=unit,
            price=price,
            description=description,
            city=city,
            photo=photo_filename
        )
        db.session.add(new_listing)
        db.session.commit()

        flash('Listing posted successfully!', 'success')
        return redirect(url_for('listing.view_listing', listing_id=new_listing.id))

    return render_template('create_listing.html',
                           material_types=MATERIAL_TYPES,
                           cities=CITIES,
                           units=UNITS)


# ── Edit listing ───────────────────────────────────────────────────────────────
@listing_bp.route('/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.user_id != session['user_id'] and not session.get('is_admin'):
        flash('You can only edit your own listings.', 'error')
        return redirect(url_for('listing.view_listing', listing_id=listing_id))

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
            return redirect(url_for('listing.edit_listing', listing_id=listing_id))

        try:
            listing.price = float(request.form.get('price', listing.price))
        except ValueError:
            flash('Price must be a number.', 'error')
            return redirect(url_for('listing.edit_listing', listing_id=listing_id))

        # New photo (optional)
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            # Remove old photo if it exists
            if listing.photo:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], listing.photo)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename    = secure_filename(photo_file.filename)
            unique_name = f"{session['user_id']}_{int(__import__('time').time())}_{filename}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
            photo_file.save(upload_path)
            listing.photo = unique_name

        db.session.commit()
        flash('Listing updated.', 'success')
        return redirect(url_for('listing.view_listing', listing_id=listing_id))

    return render_template('edit_listing.html',
                           listing=listing,
                           material_types=MATERIAL_TYPES,
                           cities=CITIES,
                           units=UNITS)


# ── Delete listing ─────────────────────────────────────────────────────────────
@listing_bp.route('/listings/<int:listing_id>/delete', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.user_id != session['user_id'] and not session.get('is_admin'):
        flash('You can only delete your own listings.', 'error')
        return redirect(url_for('listing.view_listing', listing_id=listing_id))

    # Remove photo file
    if listing.photo:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], listing.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted.', 'success')
    return redirect(url_for('listing.browse'))


# ── My listings ────────────────────────────────────────────────────────────────
@listing_bp.route('/my-listings')
@login_required
def my_listings():
    listings = Listing.query.filter_by(
        user_id=session['user_id']
    ).order_by(Listing.created_at.desc()).all()
    return render_template('my_listings.html', listings=listings)
