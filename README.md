# Recras SSL checker

Script to automatically check SSL status of your websites. Will fail if the certificate expires soon or if the SSL Labs grade is too low.

## Usage

`docker run --rm recras/sslcheck google.com github.com`

```
google.com, expires in 70 days
 - sfo07s13-in-f14.1e100.net (216.58.194.174) => A
 - sfo07s13-in-x0e.1e100.net (2607:f8b0:4005:804:0:0:0:200e) => A

github.com, expires in 446 days
 - lb-192-30-253-112-iad.github.com (192.30.253.112) => A+
 - lb-192-30-253-113-iad.github.com (192.30.253.113) => A+

Everything ok
```

Options:

```
  --mingrade TEXT             Minimum grade  [default: A]
  --mindaysremaining INTEGER  Minimum days remaining for certificates  [default: 14]
  --cache / --no-cache        Use cached results form SSL Labs  [default: True]
```
