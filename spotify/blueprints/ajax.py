
from flask import Blueprint,flash,redirect,url_for,request,render_template,current_app
from flask_login import login_required
from spotify.models import Order,Link
from multiprocessing import Process
from spotify.extendtions import db
from spotify.parse import get


ajax_bp=Blueprint('ajax',__name__)

def test(x):
    print(x)



@ajax_bp.route('/parse/order',methods=['POST','GET'])
@login_required
def new_order():
    e=request.args.get('email').strip()
    p=request.args.get('password').strip()

    while True:
        link = Link.query.filter(Link.isvalid==True).first()
        if not link:
            flash('当前没有可用链接，请添加', 'danger')
            return redirect(url_for('main.index'))
        if link.times > 0:
            break
        else:
            link.isvalid=False
            link.reason='达到使用次数上限'
            db.session.commit()

    t=Process(target=get,args=(e,p,link))
    t.start()
    flash('提交成功,正在处理','success')
    return redirect(url_for('main.index'))

@ajax_bp.route('/parse/orders',methods=['POST','GET'])
@login_required
def new_orders():


    orders=request.args.get('orders')

    infos=orders.split()
    l=int(len(infos))
    n=int(l/3)
    if l%3==0:
        for i in range(n):
            while True:
                link = Link.query.filter(Link.isvalid==True).first()
                if not link:
                    flash('当前没有可用链接，请添加', 'danger')
                    return redirect(url_for('main.index'))
                if link.times > 0:
                    break
                else:
                    link.isvalid=False
                    link.reason='达到使用次数上限'
                    db.session.commit()
            t=Process(target=get,args=(infos[i*3],infos[i*3+1],link))
            t.start()
        flash('提交完毕','success')
    else:
        flash('格式输入错误','danger')

    return redirect(url_for('main.index'))

@ajax_bp.route('/new/links',methods=['POST','GET'])
@login_required
def new_links():

    links=request.args.get('links')
    infos=links.split()
    for i in infos:
        link=Link(infos=i)
        db.session.add(link)
    db.session.commit()

    return redirect(url_for('main.index'))


@ajax_bp.route('/get/orders',methods=['POST','GET'])
@login_required
def get_orders():
    per_page=current_app.config['PER_PAGE']
    page=request.args.get('page',1)
    page=int(page)
    pagination=Order.query.filter(Order.status!='处理成功').order_by(Order.timestamp.desc()).paginate(page,per_page)
    orders=pagination.items
    return render_template('main/orders.html',orders=orders,page=page,pagination=pagination)



@ajax_bp.route('/get/detail/<order_id>',methods=['POST','GET'])
@login_required
def get_detail(order_id):

    order=Order.query.filter_by(id=order_id).first()
    orders=Order.query.filter_by(email=order.email).all()
    buy_times=len(orders)
    return render_template('main/detail_poppu.html',order=order,buy_times=buy_times)


@ajax_bp.route('/delete/link/<link_id>',methods=['POST','GET'])
@login_required
def delete_link(link_id):
    link=Link.query.get(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('删除成功','success')
    return redirect(url_for('main.links'))

@ajax_bp.route('/delete/order/<order_id>',methods=['POST','GET'])
@login_required
def delete_order(order_id):
    order=Order.query.get(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('删除成功','success')
    return redirect(url_for('main.index'))

