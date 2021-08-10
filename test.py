from datetime import datetime
import requests
import click
import sys
import time

def getResult(host, cache, startNew, maxTries = 10):
    if(maxTries < 1):
        return None

    fromCache = 'on' if cache else 'off'
    startNew = 'on' if startNew and not cache else 'off'
    r = requests.get('https://api.ssllabs.com/api/v3/analyze?host=' + host + '&fromCache=' + fromCache + '&all=done&startNew=' + startNew)
    if r.status_code in [529, 503]:
        # Service unavailable or overloaded, sleep!
        time.sleep(60 * 10)
        return getResult(host, cache, False, maxTries - 1)

    result = r.json()
    if not resultDone(result):
        time.sleep(30)
        return getResult(host, cache, False, maxTries - 1)
    return result

def resultDone(result):
    if 'status' not in result:
        return False
    return result['status'] == 'READY' or result['status'] == 'ERROR'


def analyseResult(result, mingrade, mindaysremaining):
    grades = ['A+', 'A', 'A-', 'B', 'C', 'D', 'E', 'F', 'T', 'M']
    minGradeIndex = grades.index(mingrade)
    now = datetime.utcnow()

    isOk = True
    expires = datetime.utcfromtimestamp(result['certs'][0]['notAfter'] / 1000)
    daysRemaining = (expires - now).days
    if daysRemaining < mindaysremaining:
        isOk = False

    print(result['host'] + ', expires in ' + str(daysRemaining) + ' days')
    for endpoint in result['endpoints']:
        grade = endpoint['grade'] if 'grade' in endpoint else None
        if grade is None:
            print('ERROR: Endpoint has no "grade" field')
            print(endpoint)
        if grade is None or grades.index(grade) > minGradeIndex:
            isOk = False
        serverName = endpoint['serverName'] if 'serverName' in endpoint else ''
        print(' - ' + serverName + ' (' + endpoint['ipAddress'] + ') => ' + grade)
    print()
    return isOk

@click.command()
@click.option('--mingrade', default='A', help='Minimum grade', show_default=True)
@click.option('--mindaysremaining', default=14, help='Minimum days remaining for certificates', show_default=True)
@click.option('--cache/--no-cache', default=True, help='Use cached results form SSL Labs', show_default=True)
@click.argument('hosts', nargs=-1)
def testSSL(mingrade, mindaysremaining, cache, hosts):
    hasError = False
    for host in hosts:
        result = getResult(host, cache, True)
        if not result or not analyseResult(result, mingrade, mindaysremaining):
            if not result:
                print(host + ', failed after max tries')
                print()
            hasError = True

    print('Contains errors' if hasError else 'Everything ok')
    sys.exit(hasError)


if __name__ == '__main__':
    testSSL()
