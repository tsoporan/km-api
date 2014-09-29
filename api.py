from flask import Flask
from flask import jsonify
from flask import request

from datetime import datetime
from datetime import timedelta

import os
import csv

app = Flask(__name__)

metrics_list = []

def load_data(path):
    # Load CSV data in memory.
    with open(path) as f:
        loaded = csv.reader(f.readlines())

        loaded.next() # Skip over csv header.

        # Construct date objects from starting date of Jan 1, 2009
        start_date = datetime.strptime('2009-01-01', '%Y-%m-%d')

        def format_date(days):
            return datetime.strftime(
                start_date + timedelta(days=days)
            , '%Y-%m-%d')

        for row in loaded:
            metrics_list.append({
                'metric_id'          : row[0],
                'start_date'         : format_date(int(row[1])),
                'time_range_length'  : row[2],
                'value'              : row[3],
                'last_calculated_at' : row[4],
                'end_date'           : format_date(int(row[5])),
            })

@app.route('/')
def index():
    return 'KM Demo API!'

@app.route('/metrics')
@app.route('/metrics/<int:metric_id>')
def metrics(metric_id=None):
    """
    Returns a set of metrics filtered by request params.

    Request params:

    @limit      : Number of metrics to return from offset. Default: 20
    @offset     : At what point we start counting. Default: 0
    @start_date : Metrics starting at this date. (inclusive)
    @end_date   : Metrics ending at this date. (inclusive)
    """

    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    metrics = metrics_list

    # Filtered by metric id.
    if metric_id:
        metrics = [m for m in metrics_list if int(m['metric_id']) == metric_id]

    # Filtered by date range.
    if start_date and end_date:
        try:
            requested_start_date = datetime.strptime(start_date, '%Y-%m-%d')
            requested_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify(error="Date format is incorrect, expected ISO format: YYYY-MM-DD")

        # Convert to proper date objects to compare.
        def convert_and_compare(start, end):
            metric_start = datetime.strptime(start, '%Y-%m-%d')
            metric_end   = datetime.strptime(end, '%Y-%m-%d')

            # Compare datetime objects.
            if metric_start >= requested_start_date and metric_end <= requested_end_date:
                return True

            return False

        metrics = [m for m in metrics if convert_and_compare(m['start_date'], m['end_date'])]

    # The amount of pages we can paginate.
    pages = len(metrics) / limit
    if len(metrics) % limit != 0:
        pages += 1  #Deal with overflow.

    if offset: # Make sure we keep the same limit regardless of offset.
        limit += offset

    metrics = metrics[offset:limit]

    # applicaiton/json
    return jsonify(metrics=metrics, amount=len(metrics), pages=pages)

if __name__ == '__main__':
    app.debug = True
    load_data('data/metrics_over_time_view.csv') # 'prod' data
    app.run()
