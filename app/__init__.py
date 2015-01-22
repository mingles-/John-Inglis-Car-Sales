from datetime import datetime
import os, glob
import sys

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask.ext.stormpath import (
    StormpathError,
    StormpathManager,
    User,
    login_required,
    login_user,
    logout_user,
    user,
)

from werkzeug import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/car-photos')
ALLOWED_EXTENSIONS = set(['jpg','jpeg','png','gif','JPG','JPEG','PNG','GIF'])

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'superminglesstrengthkey'
app.config['STORMPATH_API_KEY_FILE'] = 'apiKey.properties'
app.config['STORMPATH_APPLICATION'] = 'John Inglis Car Sales'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STORMPATH_ENABLE_REGISTRATION'] = False
app.config['STORMPATH_ENABLE_GIVEN_NAME'] = False
app.config['STORMPATH_ENABLE_MIDDLE_NAME'] = False
app.config['STORMPATH_ENABLE_SURNAME'] = False
app.config['STORMPATH_ENABLE_USERNAME'] = True
app.config['STORMPATH_REQUIRE_USERNAME'] = True

stormpath_manager = StormpathManager(app)

@app.route('/')
def home():
    #mrint("test home")        
    return render_template('home.html')
    
@app.route('/stocklist')
def stocklist():
    posts = []
    images = []
    mrint("test stock pre storm")
    if stormpath_manager.application.accounts == Nothing:
        mrint("not getting anything")
        
    for account in stormpath_manager.application.accounts:
        mrint("test stock post storm")
        if account.custom_data.get('posts'):
            posts.extend(account.custom_data['posts'])
            
            #for filename in glob.glob("static/car-photos/"+str(account.custom_data['posts']['numberplate'])+"_*"):
    
    for post in posts:
        var = (post['numberplate'])
        if (glob.glob("static/car-photos/"+str(var)+"_1*")):
            images.append( {'numberplate': var,
                             'path' :      glob.glob("static/car-photos/"+str(var)+"_1*")[0],
                             })
        else:
             images.append( {'numberplate': var,
                             'path' :       "static/car-photos/default.JPG",
                             })
            
    return render_template('show_posts.html', posts=posts, images=images)
    
@app.route('/findus', methods=['GET'])
def findus():
    
            
    return render_template('find_us.html')
    
@app.route('/about', methods=['GET'])
def about():
    
            
    return render_template('about.html')    

@app.route('/add', methods=['POST'])
@login_required
def add_post():
    if not user.custom_data.get('posts'):
        user.custom_data['posts'] = []

    user.custom_data['posts'].append({
        'numberplate': request.form['numberplate'],
        'make': request.form['make'],
        'model': request.form['model'],
        
    })
    user.save()

    flash('New post successfully added.')
    return redirect(url_for('show_posts'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        try:
            _user = User.from_login(
                request.form['email'],
                request.form['password'],
            )
            login_user(_user, remember=True)
            flash('You were logged in.')

            return redirect(url_for('show_posts'))
        except StormpathError, err:
            error = err.message

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out.')

    return redirect(url_for('show_posts'))


@app.route('/delete/<var>', methods=['GET', 'POST'])
@login_required
def delete(var):
    
    posts = user.custom_data['posts']
    
    # delete car information
    for post in posts:
        if str(post['numberplate']) == var:
            user.custom_data['posts'].pop(user.custom_data['posts'].index(post))
            user.save()
            
    #delete car images
    for filename in glob.glob("static/car-photos/"+var+"_*"):
        os.remove(filename)
        
    return redirect(url_for('stocklist'))

    
@app.route('/updatephotos/<var>', methods=['GET', 'POST'])
@login_required
def updatephotos(var):
    
    posts = user.custom_data['posts']
        
    for post in posts:
        if str(post['numberplate']) == var:
                            
            if request.method == 'POST':
                realImgCount=1
        
                #remove current images
                for filename in glob.glob("static/car-photos/"+var+"_*"):
                    os.remove(filename)
        
                # check if images are valid
                for i in range(1,6):
                    file = request.files['file'+str(i)]
                    if file:
                        if not(allowed_file(file.filename)):
                            return render_template('upload_error.html', errorfile=str(file.filename))
        
                # save images to car-photos folder
                for i in range(1,6):
                    file = request.files['file'+str(i)]
                    if file:
                        filename = secure_filename(file.filename)  
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], var+'_'+str(realImgCount)+'.'+filename.rsplit('.',1)[1]))
                        realImgCount += 1
                
                post['imageNumber'] = realImgCount-1
                user.save()
                       
                flash('Car Images Successfully Updated!')
                return redirect(url_for('stocklist'))
                        
            return render_template('update_photos.html', post=post)
            
    return abort(404)           

    
@app.route('/update/<var>', methods=['GET', 'POST'])
@login_required
def update(var):
    
    posts = user.custom_data['posts']
        
    for post in posts:
        if str(post['numberplate']) == var:
            
            # get extras list in nice form.
            extras = ""
            for x in post['extras']:
                extras = extras + x + ","
                            
            if request.method == 'POST':
                realImgCount=1    
                
                post['year'] = request.form['year']
                post['plate'] = request.form['plate']
                post['make'] = request.form['make']
                post['model'] = request.form['model']
                post['trim'] = request.form['trim']
                post['colour'] = request.form['colour']
                post['transmission'] = request.form['transmission']
                post['doors'] = request.form['doors']
                post['owners'] = request.form['owners']
                post['extras'] = request.form['extras'].rstrip(',').split(',')
                post['price'] = request.form['price']
                post['milage'] = request.form['milage']
                
                post['fsh'] = checkboxStatus(request.form.get('fsh'))
                post['abs'] = checkboxStatus(request.form.get('abs'))
                post['cd'] = checkboxStatus(request.form.get('cd'))
                post['ipod'] = checkboxStatus(request.form.get('ipod'))
                post['ac'] = checkboxStatus(request.form.get('ac'))
                post['em'] = checkboxStatus(request.form.get('em'))
                post['ew'] = checkboxStatus(request.form.get('ew'))
                post['cl'] = checkboxStatus(request.form.get('cl'))
                post['alloys'] = checkboxStatus(request.form.get('alloys'))
                post['fogs'] = checkboxStatus(request.form.get('fogs'))
                post['eps'] = checkboxStatus(request.form.get('eps'))
                post['pas'] = checkboxStatus(request.form.get('pas'))     
                    
                user.save()
                        
                flash('Car Information Successfully Updated!')
                return redirect(url_for('stocklist'))
        
                
            return render_template('update.html', post=post)

    return abort(404)           
                      

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
        
        
@app.route('/upload', methods = ['GET','POST'])
@login_required
def upload():

    if request.method == 'POST':
        
        # create and save car information        
        if not user.custom_data.get('posts'):
            user.custom_data['posts'] = []
            id = 1
        else:
            max = 1
            for post in user.custom_data['posts']:
                if post['numberplate'] > max:
                    max = post['numberplate']
            id = max+1
        

        user.custom_data['posts'].append({
            
            'numberplate': id,
            'year': request.form['year'],
            'plate': request.form['plate'],
            'make': request.form['make'],
            'model': request.form['model'],
            'trim': request.form['trim'],
            'colour': request.form['colour'],
            'transmission': request.form['transmission'],
            'doors': request.form['doors'],
            'owners': request.form['owners'],
            'extras': request.form['extras'].rstrip(',').split(','),
            'price': request.form['price'],
            'milage': request.form['milage'],
                           
            'fsh': checkboxStatus(request.form.get('fsh')),
            'abs': checkboxStatus(request.form.get('abs')),
            'cd': checkboxStatus(request.form.get('cd')),
            'ipod': checkboxStatus(request.form.get('ipod')),
            'ac': checkboxStatus(request.form.get('ac')),
            'em': checkboxStatus(request.form.get('em')),
            'ew': checkboxStatus(request.form.get('ew')),
            'cl': checkboxStatus(request.form.get('cl')),
            'alloys': checkboxStatus(request.form.get('alloys')),
            'fogs': checkboxStatus(request.form.get('fogs')),
            'eps': checkboxStatus(request.form.get('eps')),
            'pas': checkboxStatus(request.form.get('pas')),
            'imageNumber': 0,
            

        })
        user.save()

        flash('New car successfully added!')
        return redirect(url_for('stocklist'))
                                

    return render_template('upload.html')

def checkboxStatus(request):
    if request == None:
        return 0
    else:
        return 1


@app.route('/car/<var>', methods=['GET'])
def car(var): 
    
    posts = []
    for account in stormpath_manager.application.accounts:
        if account.custom_data.get('posts'):
            posts.extend(account.custom_data['posts'])
            
    for post in posts:
        if str(post['numberplate']) == var:
            
            images = []
            for filename in glob.glob("static/car-photos/"+var+"_*"):
                images.append(filename)
            
            extras = []
            
            if post['fsh'] == 1:
                extras.append("Full Service History")
            if post['ac'] == 1:
                extras.append("Air Conditioning")
            if post['alloys'] == 1:
                extras.append("Alloy Wheels")
            if post['abs'] == 1:
                extras.append("Anti-Lock Braking System")
            if post['pas'] == 1:
                extras.append("Power Assisted Steering")
            if post['cd'] == 1:
                extras.append("CD Player")
            if post['ipod'] == 1:
                extras.append("MP3/iPod Lead")
            if post['cl'] == 1:
                extras.append("Central Locking")
            if post['em'] == 1:
                extras.append("Electric Mirrors")
            if post['ew'] == 1:
                extras.append("Electric Windows")
            if post['eps'] == 1:
                extras.append("Electric Power Steering")
            if post['fogs'] == 1:
                extras.append("Front Fog Lights")
                    
            extras = extras + post['extras']    
            return render_template("car_display.html",post=post,images=images, extras=extras)   
    return abort(404)           

if __name__ == '__main__':
    app.run()
    
def mrint(to_print):
    print to_print
    sys.stdout.flush()
    
#stormpath = require('express-stormpath');    
'''
app.use(stormpath.init(app, {
  enableRegistration: false,
}));
'''