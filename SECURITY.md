# Security Policy

## Scope and threat model

lexilint is an offline, local teaching tool. The only security-relevant
surface is the **grader**, which executes submitted Python code
(`exec`/`eval`) on the machine running `lexilint grade`. This is intrinsic
to the design: behavior verification requires running the code.

## Safe use

- Only grade code you wrote or explicitly trust.
- Do not run `lexilint grade` on untrusted submissions from strangers on
  shared machines; use a disposable container/VM if you must.
- The tool makes no network connections and stores nothing outside the
  files you pass to it.

## Reporting

Open a GitHub issue for anything you consider a vulnerability in the
grader or CLI. Please do not include working exploit code in the issue;
describe the mechanism and share a proof of concept privately if needed.

## Supported versions

Only the latest published release receives security fixes.
