


from flask import Blueprint,render_template,request,current_app
from flask_login import login_required

from spotify.models import Order,Link



main_bp=Blueprint('main',__name__)

@main_bp.route('/',methods=['GET','POST'])
@login_required
def index():
    #

    count_num=Order.query.count()
    un_orders=Order.query.filter(Order.status!='处理成功').order_by(Order.timestamp.desc()).all()
    orders_competed=Order.query.filter(Order.status=='处理成功').order_by(Order.timestamp.desc()).limit(current_app.config['PER_PAGE'])
    links=Link.query.filter(Link.isvalid==True).all()
    num_links=len(links)
    num_uncompleted=len(un_orders)
    num_completed=count_num-num_uncompleted


    return render_template('main/index.html',orders=un_orders,num_completed=num_completed,num_links=num_links,orders_competed=orders_competed)



@main_bp.route('/links',methods=['GET','POST'])
@login_required
def links():
    #
    per_page=current_app.config['PER_PAGE']
    page=request.args.get('page',1)
    page=int(page)
    pagination=Link.query.filter(Link.isvalid==True).order_by(Link.timestamp.desc()).paginate(page,per_page)
    links=pagination.items
    pagination_bad=Link.query.filter(Link.isvalid!=True).order_by(Link.timestamp.desc()).paginate(page,per_page)
    bad_links=pagination_bad.items
    return render_template('main/links.html',links=links,page=page,pagination=pagination,pagination_bad=pagination_bad,bad_links=bad_links)