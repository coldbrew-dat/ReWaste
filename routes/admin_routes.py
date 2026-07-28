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


# ... (existing admin_required, admin_dashboard, admin_businesses, admin_listings, admin_remove_listing stay as they are)


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
