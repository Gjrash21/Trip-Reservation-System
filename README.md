Note from Khai Moffett / Person 3 : The list below is things you CANNOT change because they're locked in and will break the thing if you don't use them specifically. Like keywords and what I named stuff. If you wanna rename stuff let me know but pwetty please use these keywords

For Person 1: model field names (you loop over these in admin.html and reserve.html):
r.id
r.passengerName
r.seatRow
r.seatColumn
r.eTicketNumber
r.created

For person 1: session key (base.html checks this to show/hide the admin nav):
session.get('admin')

For person 2: route function names (used in url_for() calls in every template):
url_for('index')
url_for('reserve')
url_for('admin_login')
url_for('admin_dashboard')
url_for('admin_logout')
url_for('delete_reservation', res_id=r.id)

For person 2: variables passed into render_template (your templates expect these exact names):
# reserve.html
errors, taken, cost_matrix, col_labels, form

# admin.html
reservations, taken, cost_matrix, col_labels, total_sales, admin_user

# confirm.html
passenger_name, seat_row, seat_col, ticket, cost

# admin_login.html
error

Person 4 should be fine
