# Rule-based Root Cause Summary

The treatment improves latency, startup time, and rebuffer ratio across all observed segments. The effect appears broad-based rather than isolated to a single protocol or IP version.

## Largest absolute latency improvements by region

- US: -5.86 ms (-9.77%)
- AU: -4.04 ms (-10.11%)
- JP: -3.96 ms (-11.24%)

## Largest absolute latency improvements by edge PoP

- LAX: -5.87 ms (-9.80%)
- SJC: -5.87 ms (-9.76%)
- MEL: -4.11 ms (-10.28%)

## Protocol and IP-version pattern

- Protocol-level latency lift range: 0.16%. This suggests similar treatment effects across TCP, QUIC, and HTTP3.
- IP-version latency lift range: 0.43%. This suggests similar treatment effects across IPv4 and IPv6.

## Cost and cache-hit monitoring

- Total CDN cost difference across regions: 0.7305 USD. Cost should remain a guardrail metric during rollout.
- Cache hit rate remains close to 0.80 across most segments, so the latency gain is not clearly explained by cache-hit changes alone.

## Recommended next checks

- Re-run the experiment on a larger traffic slice.
- Monitor CDN cost, cache hit rate, startup time, and rebuffer ratio by region and edge PoP.
- Add more measured diagnostics before making lower-level network-cause claims.