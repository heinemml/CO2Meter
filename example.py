#!/usr/bin/env python3
"""Example program to get data from CO2 sensor."""
import http.server
import CO2Meter

METER = CO2Meter.CO2Meter("/dev/hidraw3")
SENSOR_LINE = """# HELP sensor_%(m)s_level Level for %(m)s.
# TYPE sensor_%(m)s_level gauge
sensor_%(m)s_level %(lvl)f
"""

class Sensor(http.server.BaseHTTPRequestHandler):
  """Class to handle sensor requests."""

  def do_GET(self):
    """Handle get requests."""
    self.send_response(200)
    self.send_header('Content-Type',
                     'text/plain; version=0.0.4; charset=utf-8')
    self.end_headers()
    levels = METER.get_data()
    for measurement in ['co2', 'temperature']:
      if measurement in levels:
        self.wfile.write(
            bytes(SENSOR_LINE % {'m': measurement,
                                 'lvl': levels[measurement]}, 'UTF-8'))


def main():
  """Main program."""
  server_address = ('', 8000)
  httpd = http.server.HTTPServer(server_address, Sensor)
  httpd.serve_forever()


if __name__ == "__main__":
  main()
