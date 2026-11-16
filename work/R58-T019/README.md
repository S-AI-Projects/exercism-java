# R58-T019 evidence

Run from the repository root:

```bash
python3 work/R58-T019/check.py
```

The reusable runner tests the maintained reference, a deliberately broken reference, and a test selection that matches no test class. It must accept the successful reference and reject both negative cases. The runner hashes learner solution files before and after, uses temporary copies, and verifies cleanup.

Detailed run statuses and test counts are written to `latest-result.json` when executed. No local execution result is claimed in this commit.
