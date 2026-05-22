% fourier_ringing_hypothesis.m
%
% User hypothesis 2026-05-21: the multi-Sylow saturation curve's
% warmup behavior is Gibbs-phenomenon ringing from the chain
% walk's sharp truncation at position 0 (no history → zero-padded
% probes).
%
% This script tests the hypothesis on a synthetic signal where
% the truth is controlled:
%
%   (a) Generate a chain-walk-like stream whose chamber indices
%       follow known periodicities at primes p ∈ {2, 3, 5, 7}.
%   (b) Apply the same multi-Sylow prime-offset sampling +
%       adaptive predictor as the codec sim.
%   (c) Measure per-position predictor cost.
%
%   Two variants of the source signal:
%     truncated:  hard zero-padded start (mirrors codec)
%     circular:   wraps around (eliminates truncation boundary)
%
%   Prediction: truncated shows ringing during first ~max(prime)
%   positions; circular does not. If true, the codec's warmup
%   behavior is structural Fourier truncation, not corpus-specific.

%% Build synthetic chain-walk stream
%
% Each chamber index ∈ {0..23} is determined by a deterministic
% function of position n: chamber(n) = (multi-period sum) mod 24.
% Periods chosen at primes 2, 3, 5, 7 to inject structure these
% Sylow probes should detect.

N = 4096;
n = 0:N-1;

% Multi-period chain: sum of mod-p contributions, then mod 24.
chain = mod(n*5 + 3*mod(n,2) + 5*mod(n,3) + 7*mod(n,5) + 11*mod(n,7), 24);

% Variants:
chain_truncated = chain;            % zero-pad at start (codec model)
chain_circular  = [chain(end-30:end), chain]; % wrap last 31 to front
chain_circular  = chain_circular(1:N);

%% V₄-part extraction (matches Python coarse_residue's V₄-coset position)
%
% For tractability in Octave, approximate V₄-part = chamber mod 4.
% This is an order-of-magnitude approximation of the actual coset
% structure but preserves the 4-value range and arithmetic.

v4_part = @(c) mod(c, 4);

%% Joint multi-Sylow context

function ctx = joint_context(chain, primes)
    N = length(chain);
    ctx = zeros(1, N);
    for k = 1:N
        v = 0;
        for i = 1:length(primes)
            p = primes(i);
            pos = k - p;
            if pos < 1
                crumb = 0;
            else
                crumb = mod(chain(pos), 4);
            end
            v = v + bitshift(crumb, 2*(i-1));
        end
        ctx(k) = v;
    end
end

%% Adaptive predictor with Laplace smoothing

function costs = predictor_cost(chain, ctx_stream)
    N = 24;
    alpha = 0.5;
    n_ctx = max(ctx_stream) + 1;
    counts = zeros(n_ctx, N);
    L = length(chain);
    costs = zeros(1, L);
    for k = 1:L
        emit = chain(k) + 1;       % 1-indexed
        ctx = ctx_stream(k) + 1;
        total = sum(counts(ctx, :)) + alpha * N;
        p = (counts(ctx, emit) + alpha) / total;
        costs(k) = -log2(p);
        counts(ctx, emit) = counts(ctx, emit) + 1;
    end
end

%% Rolling mean

function r = rolling_mean(x, w)
    if length(x) < w
        r = x;
        return;
    end
    cs = cumsum([0 x]);
    r = (cs(w+1:end) - cs(1:end-w)) / w;
end

%% Run experiment

primes = [2, 3, 5, 7];

ctx_trunc = joint_context(chain_truncated, primes);
ctx_circ  = joint_context(chain_circular,  primes);

cost_trunc = predictor_cost(chain_truncated, ctx_trunc);
cost_circ  = predictor_cost(chain_circular,  ctx_circ);

% Summary: mean cost in windows
window_size = 64;
fprintf("\nFourier-ringing test on synthetic chain-walk signal\n");
fprintf("  Length N = %d, primes = %s\n\n", N, mat2str(primes));
fprintf("Mean cost (bits) by position window:\n");
fprintf("  %-22s  %10s  %10s  %10s\n", ...
        "predictor", "first 64", "pos 500-1500", "pos 3000+");

regions = struct( ...
    "first_64",      1:64, ...
    "pos_500_1500",  500:1500, ...
    "pos_3000_plus", 3000:N);

fields = {"first_64", "pos_500_1500", "pos_3000_plus"};
for which = {"truncated", "circular"}
    if strcmp(which{1}, "truncated")
        c = cost_trunc;
    else
        c = cost_circ;
    end
    fprintf("  %-22s", which{1});
    for f = fields
        idx = getfield(regions, f{1});
        fprintf("  %10.3f", mean(c(idx)));
    end
    fprintf("\n");
end

% Save the per-position cost data for plotting.
csv_path = "/tmp/octave_fourier_ringing.csv";
fid = fopen(csv_path, "w");
fprintf(fid, "position,cost_truncated,cost_circular\n");
for k = 1:N
    fprintf(fid, "%d,%.4f,%.4f\n", k, cost_trunc(k), cost_circ(k));
end
fclose(fid);
fprintf("\nCSV saved: %s\n", csv_path);

% Quick ASCII plot of rolling means
fprintf("\nRolling mean (window=64):\n");
rm_trunc = rolling_mean(cost_trunc, 64);
rm_circ  = rolling_mean(cost_circ,  64);
y_min = min([rm_trunc, rm_circ]);
y_max = max([rm_trunc, rm_circ]);
n_show = min(length(rm_trunc), 60);
step = max(1, floor(length(rm_trunc) / n_show));
height = 10;
for label_data = {{"truncated", rm_trunc}, {"circular", rm_circ}}
    label = label_data{1}{1};
    data = label_data{1}{2};
    fprintf("  %s (y-range [%.2f, %.2f]):\n", label, y_min, y_max);
    for r = height-1:-1:0
        line = sprintf("    %5.2f|", y_min + r/(height-1) * (y_max-y_min));
        for col = 0:n_show-1
            pos = col*step + 1;
            if pos > length(data)
                line = [line " "];
                continue;
            end
            val = data(pos);
            norm = (val - y_min) / (y_max - y_min);
            target = round(norm * (height-1));
            if target >= r
                line = [line "#"];
            else
                line = [line " "];
            end
        end
        fprintf("%s\n", line);
    end
    fprintf("          %s\n", repmat("-", 1, n_show));
end

fprintf("\nDone.\n");
