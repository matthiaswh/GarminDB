#!/usr/bin/env python

#
# copyright Tom Goetz
#

import os, sys, getopt, re, string, logging, datetime

import GarminSqlite


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)


class Analyze():

    def __init__(self, dbpath):
        self.mondb = GarminSqlite.MonitoringDB(dbpath)
        self.sumdb = GarminSqlite.MonitoringSummaryDB(dbpath)

    def get_years(self):
        years = GarminSqlite.MonitoringHeartRate.get_years(self.mondb)
        GarminSqlite.Summary.create_or_update(self.sumdb, {'name' : 'years', 'value' : len(years)})
        print "Years (%d): %s" % (len(years), str(years))

    def get_months(self, year):
        months = GarminSqlite.MonitoringHeartRate.get_month_names(self.mondb, year)
        GarminSqlite.Summary.create_or_update(self.sumdb, {'name' : year + '_months', 'value' : len(months)})
        print "%s Months (%d): %s" % (year, len(months) , str(months))

    def get_days(self, year):
        days = GarminSqlite.MonitoringHeartRate.get_days(self.mondb, year)
        days_count = len(days)
        if days_count > 0:
            first_day = days[0]
            last_day = days[-1]
            span = last_day - first_day + 1
        else:
            span = 0
        GarminSqlite.Summary.create_or_update(self.sumdb, {'name' : year + '_days', 'value' : days_count})
        GarminSqlite.Summary.create_or_update(self.sumdb, {'name' : year + '_days_span', 'value' : span})
        print "%s Days (%d vs %d): %s" % (year, days_count, span, str(days))

    def summary(self):
        years = GarminSqlite.MonitoringHeartRate.get_years(self.mondb)
        for year in years:
            days = GarminSqlite.MonitoringHeartRate.get_days(self.mondb, year)
            for day in days:
                day_ts = datetime.datetime(year, 1, 1) + datetime.timedelta(day - 1)
                stats = GarminSqlite.MonitoringHeartRate.get_daily_stats(self.mondb, day_ts)
                stats.update(GarminSqlite.MonitoringClimb.get_daily_stats(self.mondb, day_ts))
                stats.update(GarminSqlite.MonitoringIntensityMins.get_daily_stats(self.mondb, day_ts))
                stats.update(GarminSqlite.Monitoring.get_daily_stats(self.mondb, day_ts))
                GarminSqlite.DaysSummary.create_or_update(self.sumdb, stats)
            for week_starting_day in xrange(1, 365, 7):
                day_ts = datetime.datetime(year, 1, 1) + datetime.timedelta(week_starting_day - 1)
                stats = GarminSqlite.MonitoringHeartRate.get_weekly_stats(self.mondb, day_ts)
                stats.update(GarminSqlite.MonitoringClimb.get_weekly_stats(self.mondb, day_ts))
                stats.update(GarminSqlite.MonitoringIntensityMins.get_weekly_stats(self.mondb, day_ts))
                stats.update(GarminSqlite.Monitoring.get_weekly_stats(self.mondb, day_ts))
                GarminSqlite.WeeksSummary.create_or_update(self.sumdb, stats)


def usage(program):
    print '%s -d <dbpath> -m ...' % program
    sys.exit()

def main(argv):
    dbpath = None
    years = False
    months = None
    days = None
    summary = False

    try:
        opts, args = getopt.getopt(argv,"d:i:m:sy", ["dbpath=", "days=", "months=", "years", "summary"])
    except getopt.GetoptError:
        usage(sys.argv[0])

    for opt, arg in opts:
        if opt == '-h':
            usage(sys.argv[0])
        elif opt in ("-d", "--dbpath"):
            logging.debug("DB path: %s" % arg)
            dbpath = arg
        elif opt in ("-y", "--years"):
            logging.debug("Years")
            years = True
        elif opt in ("-m", "--months"):
            logging.debug("Months")
            months = arg
        elif opt in ("-d", "--days"):
            logging.debug("Days")
            days = arg
        elif opt in ("-s", "--summary"):
            logging.debug("Summary")
            summary = True

    if not dbpath:
        print "Missing arguments:"
        usage(sys.argv[0])

    analyze = Analyze(dbpath)
    if years:
        analyze.get_years()
    if months:
        analyze.get_months(months)
    if days:
        analyze.get_days(days)
    if summary:
        analyze.summary()

if __name__ == "__main__":
    main(sys.argv[1:])

