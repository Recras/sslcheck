from datetime import datetime
import requests
import click
import sys
import time

def getResult(host, cache):
    fromCache = 'on' if cache else 'off'
    r = requests.get('https://api.ssllabs.com/api/v3/analyze?host=' + host + '&fromCache=' + fromCache + '&all=done')
    return r.json()

def resultDone(result):
    return result['status'] == 'READY' or result['status'] == 'ERROR'

@click.command()
@click.option('--mingrade', default='A', help='Minimum grade', show_default=True)
@click.option('--mindaysremaining', default=14, help='Minimum days remaining for certificates', show_default=True)
@click.option('--cache/--no-cache', default=True, help='Use cached results form SSL Labs', show_default=True)
@click.argument('hosts', nargs=-1)
def testSSL(mingrade, mindaysremaining, cache, hosts):
    grades = ['A+', 'A', 'A-', 'B', 'C', 'D', 'E', 'F', 'T', 'M']
    minGradeIndex = grades.index(mingrade)
    now = datetime.utcnow()
    hasError = False

    for host in hosts:
        result = getResult(host, cache)
        while not resultDone(result):
            time.sleep(30)
            result = getResult(host, cache)

        expires = datetime.utcfromtimestamp(min(map(lambda cert: cert['notAfter'],result['certs'])) / 1000)
        daysRemaining = (expires - now).days
        if daysRemaining < mindaysremaining:
            hasError = True

        print(result['host'] + ', expires in ' + str(daysRemaining) + ' days')
        for endpoint in result['endpoints']:
            grade = endpoint['grade']
            if grades.index(grade) > minGradeIndex:
                hasError = True
            print(' - ' + endpoint['serverName'] + ' (' + endpoint['ipAddress'] + ') => ' + grade)
        print()

    print('Contains errors' if hasError else 'Everything ok')
    sys.exit(hasError)


if __name__ == '__main__':
    testSSL()
