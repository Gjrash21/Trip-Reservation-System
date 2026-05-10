from flask import Flask, render_template, request, redirect, url_for, session, flash
app = Flask(__name__)
app.secret_key = 'secret-key-hehe'

def create_cost_matrix():
    costs = [100, 75, 50, 100]
    return [[costs[col] for col in range(4)] for row in range(12)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    '''
    create matrix
    make sure labels align with readme
    '''
    cost_matrix = create_cost_matrix()
    col_labels = ['A', 'B', 'C', 'D']
    errors = [] #create a variable to hold errors

    #step 1 - grab data from form
    if request.method == 'POST':
         first_name = request.form.get('first_name', '').strip()
         last_name = request.form.get('last_name', '').strip()
         seat_row = request.form.get('seat_row', '').strip()
         seat_col = request.form.get('seat_col', '').strip().upper()

    # error check
    if not first_name:
         errors.append('First name is required.')
    if not last_name:
         errors.append('Last name is required.')

    if not seat_row:
         errors.append('Insert a seat row.')
    if not seat_row >= 1 & seat_row <= 12:
         errors.append('Choose a valid row option.')

    if not seat_col:
         errors.append('Insert a seat column.')
    if not seat_col == ['A', 'B', 'C', 'D']:
         errors.append('Choose valid seat option.')
    
    if errors:
         return render_template('reserve.html',
                           errors=errors,
                           taken={},
                           cost_matrix=cost_matrix,
                           col_labels=col_labels,
                           form=request.form)





    return render_template('reserve.html',
                           errors=[],
                           taken={},
                           cost_matrix=cost_matrix,
                           col_labels=col_labels,
                           form={}
                           )

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
      '''
        login page

        GET & POST Methods utilized
        url_for to redirect
        '''
      if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')

            if username == 'admin' and password == 'password':
                session['admin'] = username
                flash(f'Welcome, {username}!')
                return redirect(url_for('admin_dashboard'))
                
            else: 
                return render_template('admin_login.html', error='Invalid credentials, please try again.')
    
      return render_template('admin_login.html', error=None)

@app.route('/admin')
def admin_dashboard():
        if not session.get('admin'):
             return redirect(url_for('admin_login'))
        
        cost_matrix = create_cost_matrix()
        col_labels = ['A', 'B', 'C', 'D']
        

        return render_template('admin.html',
                               reservations=[],
                               taken={},
                               cost_matrix=cost_matrix,
                               col_labels=col_labels,
                               total_sales=0,
                               admin_user=session.get('admin'))

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/delete/<int:res_id>', methods=['POST'])
def delete_reservation(res_id):
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)