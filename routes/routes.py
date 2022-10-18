from flask import Blueprint
from controllers.controllers import show_table, ticker, ticker_list, re

user_bp = Blueprint('user_bp', __name__)

user_bp.route('/')(re)

user_bp.route('/show_all/')(show_table)

user_bp.route('/<int:ticker_id>/ticker/', methods=('GET', 'POST'))(ticker)

user_bp.route('/<int:ticker_id>/ticker_list/', methods=('GET', 'POST'))(ticker_list)
