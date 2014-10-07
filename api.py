from flask import Flask
from flask import jsonify
from flask import request

from datetime import datetime
from datetime import timedelta

import os
import csv

app = Flask(__name__)

# Construct date objects from starting date of Jan 1, 2009
API_START_DATE = datetime.strptime('2009-01-01', '%Y-%m-%d')

# Metrics loaded in memory.
METRICS = []

def load_data(path):
    with open(path) as f:
        loaded = csv.reader(f.readlines())

        loaded.next() # Skip over csv header.

        for row in loaded:
            METRICS.append({
                'metric_id'          : row[0],
                'start_date'         : format_date(int(row[1])),
                'time_range_length'  : row[2],
                'value'              : row[3],
                'last_calculated_at' : row[4],
                'end_date'           : format_date(int(row[5])),
            })

def format_date(days):
    return datetime.strftime(
        API_START_DATE + timedelta(days=days)
    , '%Y-%m-%d')

def convert_and_compare(start, end, compare_start, compare_end):
    # Convert to proper date objects to compare.
    metric_start = datetime.strptime(start, '%Y-%m-%d')
    metric_end   = datetime.strptime(end, '%Y-%m-%d')

    # Compare datetime objects.
    if metric_start >= compare_start and metric_end <= compare_end:
        return True

    return False


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

    metrics = METRICS

    # Filtered by metric id.
    if metric_id:
        metrics = [m for m in metrics if int(m['metric_id']) == metric_id]

    # Filtered by date range.
    if start_date and end_date:
        try:
            compare_start = datetime.strptime(start_date, '%Y-%m-%d')
            compare_end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify(error="Date format is incorrect, expected ISO format: YYYY-MM-DD")

        metrics = [m for m in metrics if convert_and_compare(m['start_date'], m['end_date'], compare_start, compare_end)]

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

    data_path = 'data/metrics_over_time_view.csv' # 'prod' data

    load_data(data_path)

    app.run()
