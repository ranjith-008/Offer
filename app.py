from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from models import db, Bus, BusSeat, Video, GlobalSettings

app = Flask(__name__)
app.secret_key = "TMB"
ADMIN_SECRET_KEY = "TMB"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://aimuniverss_user:Sabari08@localhost/offer_management'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ZNISCGoelVhglruNxeQhJwxRPCpCvuZC@mysql.railway.internal:3306/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure tables are created    
with app.app_context():
    db.create_all()
    
    # Initialize Global Settings if not exists
    if not GlobalSettings.query.first():
        db.session.add(GlobalSettings(total_booked_tickets=0, savings_per_ticket=0))
        db.session.commit()



UPLOAD_FOLDER = 'static/videos'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/owner')
def owner_home():
    global_stats = GlobalSettings.query.first()
    return render_template('home.html', global_stats=global_stats)

@app.route('/update-global-stats', methods=['POST'])
def update_global_stats():
    admin_key = request.form.get('admin_key')
    if admin_key != ADMIN_SECRET_KEY:
        flash("Invalid admin secret key!", "danger")
        return redirect('/owner')

    stats = GlobalSettings.query.first()
    if stats:
        stats.total_booked_tickets = request.form.get('total_booked_tickets', 0)
        stats.savings_per_ticket = request.form.get('savings_per_ticket', 0)
        db.session.commit()
        flash("Global statistics updated successfully!", "success")
    
    return redirect('/owner')

#create bus offers
@app.route('/add-bus', methods=['GET', 'POST'])
def add_bus():
    if request.method == 'POST':
        admin_key = request.form.get('admin_key')
        if admin_key != ADMIN_SECRET_KEY:
            flash("Invalid admin secret key!", "danger")
            return redirect('/add-bus')

        # 1️⃣ SAVE BUS
        bus = Bus(
            bus_name=request.form['bus_name'],
            bus_type=request.form['bus_type'],
            from_location=request.form['from_location'],
            to_location=request.form['to_location'],
            journey_date=request.form['journey_date'],
            start_time=request.form['start_time'],
            reach_time=request.form['reach_time']
        )
        db.session.add(bus)
        db.session.commit()   # VERY IMPORTANT

        # 2️⃣ SAVE SEAT PRICES
        seat_types = ['USS', 'LSS', 'UDS', 'LDS', 'SS']

        for seat in seat_types:
            price = request.form.get(f'price_{seat}')
            if price:   # save only if owner entered price
                seat_obj = BusSeat(
                    bus_id=bus.id,
                    seat_type=seat,
                    price=price
                )
                db.session.add(seat_obj)

        db.session.commit()

        flash("Bus and seat prices added successfully!", "success")
        return redirect('/buses/')

    return render_template('add_bus.html')

@app.route('/buses/')
def owner_buses():
    buses = Bus.query.all()
    return render_template('buses.html', buses=buses)

#update existing offers
@app.route('/edit-bus/<int:id>', methods=['GET', 'POST'])
def edit_bus(id):
    bus = Bus.query.get_or_404(id)
    seats = BusSeat.query.filter_by(bus_id=id).all()

    if request.method == 'POST':
        admin_key = request.form.get('admin_key')

        if admin_key != ADMIN_SECRET_KEY:
            flash("Invalid admin secret key!", "danger")
            return redirect(f'/edit-bus/{id}')
        # update bus
        bus.bus_name = request.form['bus_name']
        bus.bus_type = request.form['bus_type']
        bus.from_location = request.form['from_location']
        bus.to_location = request.form['to_location']
        bus.journey_date = request.form['journey_date']
        bus.start_time = request.form['start_time']
        bus.reach_time = request.form['reach_time']

        # update seat prices
        for seat in seats:
            price = request.form.get(f'price_{seat.id}')
            if price:
                seat.price = price

        db.session.commit()
        flash("Bus and seat prices updated successfully!", "success")
        return redirect('/buses/')

    return render_template('update_bus.html', bus=bus, seats=seats)


#delete offers
@app.route('/delete-bus/<int:id>', methods=['POST'])
def delete_bus(id):
    admin_key = request.form.get('admin_key')

    if admin_key != ADMIN_SECRET_KEY:
        flash("Invalid admin secret key!", "danger")
        return redirect('/buses/')

    bus = Bus.query.get_or_404(id)
    db.session.delete(bus)
    db.session.commit()

    flash("Bus deleted successfully!", "success")
    return redirect('/buses/')


@app.route('/')
def user_buses():
    buses = Bus.query.all()
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('user_buses.html', buses=buses, videos=videos)


@app.route('/upload-video', methods=['POST'])
def upload_video():
    admin_key = request.form.get('admin_key')
    if admin_key != ADMIN_SECRET_KEY:
        flash("Invalid admin secret key!", "danger")
        return redirect('/owner')

    if 'video' not in request.files:
        flash("No video part", "danger")
        return redirect('/owner')
    
    file = request.files['video']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect('/owner')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Save to DB
        new_video = Video(filename=filename)
        db.session.add(new_video)
        db.session.commit()
        
        flash("Video uploaded successfully!", "success")
        return redirect('/owner')
    
    flash("Invalid file type. Only MP4, MOV, AVI, MKV allowed.", "danger")
    return redirect('/owner')


@app.route('/manage-videos')
def manage_videos():
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return render_template('manage_videos.html', videos=videos)


@app.route('/delete-video/<int:id>', methods=['POST'])
def delete_video(id):
    admin_key = request.form.get('admin_key')
    if admin_key != ADMIN_SECRET_KEY:
        flash("Invalid admin secret key!", "danger")
        return redirect('/manage-videos')

    video = Video.query.get_or_404(id)
    filename = video.filename
    
    # Try to delete from filesystem first
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_deleted = False
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            file_deleted = True
        except PermissionError:
            # File is likely being used by the server or browser
            pass
        except Exception as e:
            flash(f"Error deleting file: {e}", "warning")
    
    # Always delete from DB so it's removed from UI
    db.session.delete(video)
    db.session.commit()
    
    if file_deleted:
        flash(f"Video '{filename}' deleted successfully!", "success")
    else:
        flash(f"Video record removed, but the file '{filename}' is currently in use and couldn't be deleted. It will be ignored by the system.", "info")
        
    return redirect('/manage-videos')

# API Endpoint for Live Updates
@app.route('/api/buses')
def api_buses():
    buses = Bus.query.all()
    bus_list = []
    for bus in buses:
        seats = sorted([{
            'seat_type': s.seat_type,
            'price': s.price
        } for s in bus.seats], key=lambda x: x['price'])
        
        bus_list.append({
            'id': bus.id,
            'bus_name': bus.bus_name,
            'bus_type': bus.bus_type,
            'from_location': bus.from_location,
            'to_location': bus.to_location,
            'journey_date': str(bus.journey_date),
            'start_time': str(bus.start_time),
            'reach_time': str(bus.reach_time),
            'booked_seats': bus.booked_seats,
            'seats': seats,
            'min_price': seats[0]['price'] if seats else 0
        })
    return jsonify(bus_list)


@app.route('/api/global-stats')
def api_global_stats():
    stats = GlobalSettings.query.first()
    return jsonify({
        'total_booked': stats.total_booked_tickets if stats else 0,
        'savings_per_ticket': stats.savings_per_ticket if stats else 0
    })


if __name__ == '__main__':
    app.run(debug=True)
