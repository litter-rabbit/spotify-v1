


from flask import Blueprint,render_template,request,current_app,flash,redirect,url_for
from spotify.models import Order,Link
from spotify.extendtions import db
import datetime


main_bp=Blueprint('main',__name__)

@main_bp.route('/',methods=['GET','POST'])
def index():
    #
    dat = datetime.date.today()
    un_orders=Order.query.filter(Order.status!='处理成功').order_by(Order.timestamp.desc()).all()
    # orders_competed=Order.query.filter(Order.status=='处理成功').order_by(Order.timestamp.desc()).limit(current_app.config['PER_PAGE'])
    orders_competed = Order.query.filter(db.cast(Order.timestamp,db.DATE)==dat and Order.status=='处理成功').order_by(Order.timestamp.desc()).limit(current_app.config['PER_PAGE'])
    links=Link.query.filter(Link.isvalid==True).all()
    num_links=len(links)
    num_completed = Order.query.filter(db.cast(Order.timestamp,db.DATE)==dat and Order.status=='处理成功').count()

    return render_template('main/index.html',orders=un_orders,num_completed=num_completed,num_links=num_links,orders_competed=orders_competed)



@main_bp.route('/links',methods=['GET','POST'])
def links():
    per_page=current_app.config['PER_PAGE']
    page=request.args.get('page',1)
    page=int(page)
    pagination=Link.query.filter(Link.isvalid==True).order_by(Link.timestamp.desc()).paginate(page,per_page)
    links=pagination.items
    pagination_bad=Link.query.filter(Link.isvalid!=True).order_by(Link.timestamp.desc()).paginate(page,per_page)
    bad_links=pagination_bad.items
    return render_template('main/links.html',links=links,page=page,pagination=pagination,pagination_bad=pagination_bad,bad_links=bad_links)


@main_bp.route('/search',methods=['GET','POST'])
def search():
    per_page = current_app.config['PER_PAGE']
    page = request.args.get('page', 1)
    page = int(page)
    email=request.args.get('email')
    if not email or len(email)<=0:
        flash('查询内容不能为空','danger')
        return redirect(url_for('main.search_order'))
    if '@' in email:
        q=email.split('@')
        email=q[0]
    pagination=Order.query.whooshee_search(email).filter(Order.status=='处理成功').order_by(Order.timestamp.desc()).paginate(page,per_page)
    orders=pagination.items
    num_orders=len(orders)
    return render_template('main/seach_order.html',orders=orders,page=page,pagination=pagination,num_orders=num_orders)


@main_bp.route('/orders',methods=['GET','POST'])
def search_order():

    per_page=current_app.config['PER_PAGE']
    page=request.args.get('page',1)
    page=int(page)
    pagination=Order.query.filter(Order.status=='处理成功').order_by(Order.timestamp.desc()).paginate(page,per_page)
    # pagination=Order.query.order_by(Order.timestamp.desc()).paginate(page,per_page)
    orders=pagination.items
    num_orders=len(orders)
    return render_template('main/seach_order.html',orders=orders,page=page,pagination=pagination,num_orders=num_orders)





