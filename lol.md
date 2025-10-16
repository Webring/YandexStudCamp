# Distilling an autoregressive coding Transformer into a masked diffusion language model (LLaDA-style)

This guide explains how to use an autoregressive (AR) Transformer teacher’s logits to train a smaller masked diffusion language model (MDM) student, following the LLaDA approach. It focuses on defining a knowledge-distillation (KD) loss that replaces hard targets with teacher soft targets for masked tokens, and on reconciling the student’s bidirectional conditioning with the teacher’s left-to-right nature.

- **Takeaway**: Yes, you can distill across different architectures. The core KD loss is a masked-token KL between teacher and student distributions. The main challenge is getting “bidirectional” soft targets from a left-to-right teacher; we provide exact and approximate solutions.
- **Recommended**: If your coding LLM supports fill-in-the-middle (FIM), use it to obtain bidirectional teacher logits directly. Otherwise, use suffix scoring with top-K tokens.

## Notation

- \(x_0 = (x_1,\dots,x_L)\): token sequence from the training corpus.
- \(t \sim \mathcal{U}(0,1)\): mask ratio.
- \(x_t\): sequence where each token is independently masked with probability \(t\).
- M: special mask token.
- Student: \(p_\theta(\cdot \mid x_t)\), predicts masked tokens simultaneously from bidirectional visible context.
- Teacher: an AR Transformer producing next-token logits left-to-right.

For SFT (prompt-response), split \(x_0 = [p_0; r_0]\), and only mask in \(r_0\).

## 1) Baseline MDM objective (no KD)

LLaDA trains with masked-token cross-entropy on masked positions only, which upper-bounds \(-\mathbb{E}\log p_\theta(x_0)\) and does not require time as input.

- Unconditional pretraining:
\[
\mathcal{L}_{\text{MDM}}
= \mathbb{E}_{x_0,\,t,\,x_t}\left[
 - \frac{1}{L}\sum_{i=1}^L \mathbf{1}[x_i=\text{M}] \log p_\theta(x_i \mid x_t)
\right]
\]

- Conditional/SFT (only mask response):
\[
\mathcal{L}_{\text{MDM-cond}}
= \mathbb{E}_{(p_0,r_0),\,t,\,r_t}\left[
 - \frac{1}{|r_0|}\sum_{i \in \text{resp}} \mathbf{1}[r_i=\text{M}] \log p_\theta(r_i \mid p_0, r_t)
\right]
\]

Low-variance equivalent Monte Carlo masking (mask exactly \(l\) tokens) can be used for evaluation and also works well for training:
\[
\mathcal{L}_{\text{MDM-eq}}
= \mathbb{E}_{x_0,\,l,\,x_l}\left[
 - \frac{1}{L}\sum_{i=1}^L \mathbf{1}[x_i=\text{M}] \log p_\theta(x_i \mid x_l)
\right]
\]
where \(l \sim \{1,\dots,L\}\), and \(x_l\) masks exactly \(l\) positions uniformly.

## 2) KD objective: replace hard labels with teacher soft targets

Define a teacher distribution \(q_T(\cdot \mid \text{context}_i)\) for each masked position \(i\). Replace the hard one-hot target with a KL:

\[
\mathcal{L}_{\text{KD}}
= \mathbb{E}\left[
 \frac{1}{L}\sum_{i=1}^L \mathbf{1}[x_i=\text{M}]\;
 T^2\;\mathrm{KL}\!\left(
   q_T(\cdot \mid \text{context}_i)
   \;\Vert\;
   p_\theta^T(\cdot \mid x_t)
 \right)
\right]
\]

- Temperature \(T\): apply to both teacher and student logits; use \(T^2\) scaling to stabilize gradients.
- Combine with the hard-label loss (ramp \( \lambda \) over training):
\[
\mathcal{L}
= (1-\lambda)\,\mathcal{L}_{\text{MDM or MDM-cond}}
 + \lambda\,\mathcal{L}_{\text{KD}}
\]
Typical: start \(\lambda=0.2\), increase to 0.7–1.0; \(T\in[1,4]\) for code.

## 3) Getting bidirectional soft targets from a left-to-right teacher

The student needs \(q_T(x_i \mid \text{left},\text{right})\). The AR teacher natively gives \(p_T(\cdot \mid \text{left})\). Use:

\[
p_T(x_i=v \mid \text{left}, \text{right})
\;\propto\;
p_T(v \mid \text{left})\;\cdot\; p_T(\text{right} \mid \text{left}, v)
\]

- Compute next-token dist: \(p_T(v \mid \text{left})\).
- Score the observed suffix (gold right context) given the hypothesized token \(v\):
\[
\log p_T(\text{right} \mid \text{left}, v) = \sum_{j=i+1}^{L} \log p_T(x_j \mid \text{left}, v, x_{i+1:j-1})
\]
- Combine in log-space and normalize over \(v\) (e.g., top-K):
\[
s(v) = \log p_T(v \mid \text{left}) + \log p_T(\text{right} \mid \text{left}, v), \quad
q_T(v \mid \text{left}, \text{right}) = \mathrm{softmax}_v\big(s(v)/T\big)
\]

This is exact for a single masked token. For spans, see below.

### If your teacher supports FIM (recommended for code LMs)
Use a FIM prompt (prefix/middle/suffix). The teacher’s logits for the first middle token directly approximate \(p_T(\cdot \mid \text{left}, \text{right})\), avoiding suffix-scoring loops. For multi-token spans, roll forward within the hole token-by-token.

### Span masks
Exact bidirectional targets over long spans are expensive. Practical options:
- KD only on 1 masked token per example and train other masked tokens with hard CE; rotate positions across steps.
- Keep spans short (e.g., 1–3 tokens).
- FIM: predict the middle region sequentially using teacher logits conditioned on both sides.
- Approximate: inside-span left-to-right factorization with occasional reweighting by suffix likelihood of the remainder.

### If suffix scoring is too costly
Fallbacks:
- Use \(p_T(\cdot \mid \text{left})\) as \(q_T\). This conditioning mismatch is acceptable when mixed with hard CE; still provides useful soft supervision.
- Few-shot prompt the teacher to emulate infill (less stable than true FIM).

## 4) Tokenizer considerations

- Prefer sharing the tokenizer between teacher and student. This makes the KL well-defined token-wise.
- If tokenizers differ, map distributions:
  - Upstream choice: train the student on the teacher’s tokenizer (simplest).
  - Otherwise, approximate a mapping by splitting teacher tokens to student subpieces and distributing probability mass (can be lossy), or move KD to the embedding space (cosine/`L2` on logits projected into a shared subword space). For code, sharing tokenizer is strongly recommended.

## 5) Practical training recipe

- Masking:
  - Pretraining: sample \(t \sim \mathcal{U}(0,1)\) and mask independently, or sample \(l\) and mask exactly \(l\) tokens (lower variance).
  - SFT: only mask response tokens; append and later strip `|EOS|` to learn length control.
- KD sampling:
  - Per batch, pick a subset of masked positions (e.g., 1–4 per sequence) for KD to control teacher compute; others use hard CE.
  - For each KD position, build \(q_T\) with FIM or suffix scoring on top-K candidates (e.g., K∈[32,256]).
- Loss:
  - Use \(\mathcal{L}=(1-\lambda)\,\text{CE}_{\text{masked}} + \lambda\,T^2\,\text{KL}(q_T || p_\theta^T)\).
  - Optionally add `label_smoothing` (e.g., 0.05) on the CE branch early in training.
- Optimization:
  - Follow LLaDA schedules (e.g., warmup-stable-decay; AdamW with weight decay 0.1).
  - Gradient clip (e.g., 1.0). Use EMA for stability if the student is very small.
- Inference alignment:
  - Train with the same remasking strategies you’ll use at inference (random remasking; for instruct, consider low-confidence + semi-autoregressive blocks as in LLaDA).
  - Consider unsupervised classifier-free guidance at inference; not needed for training.

## 6) Pseudocode (KD on a subset of masked positions)

```python
# Inputs: batch of tokenized sequences x0 [B, L]
# mask either with t~U(0,1) per sample or exactly l positions
xt, mask = apply_mask(x0)  # mask bool [B, L], True where token is masked

# Student forward
stud_logits = student(xt)            # [B, L, V]
stud_logits_T = stud_logits / T
stud_probs_T = softmax(stud_logits_T, dim=-1)

# Select a small subset of masked positions per sequence for KD
kd_positions = sample_kd_positions(mask, max_kd_per_seq=2)

kl_total, ce_total, count_kl, count_ce = 0.0, 0.0, 0, 0
for b, i in kd_positions:
    left  = x0[b, :i]
    right = x0[b, i+1:]
    # Teacher target q_T: prefer FIM; else suffix scoring with top-K
    q_logits = get_teacher_bidirectional_logits(left, right, top_k=128)  # [V]
    q_T = softmax(q_logits / T, dim=-1)

    p_T = stud_probs_T[b, i]  # [V]
    kl_total += kl_div(q_T, p_T)   # forward KL
    count_kl += 1

# Hard CE on remaining masked positions (or all masked positions)
for b in range(B):
    for i in range(L):
        if mask[b, i]:
            y = x0[b, i]
            ce_total += cross_entropy(stud_logits[b, i], y)
            count_ce += 1

loss = 0.0
if count_ce > 0:
    loss += (1 - lambda_kd) * (ce_total / count_ce)
if count_kl > 0:
    loss += lambda_kd * (T*T) * (kl_total / count_kl)

loss.backward()
optimizer.step()
```

Notes:
- `get_teacher_bidirectional_logits`:
  - FIM path: one teacher forward on a `<prefix><FIM_MIDDLE><suffix>` template.
  - Suffix-scoring path: get `log p_T(v|left)` (single step), then sum `log p_T(right | left, v)` using teacher’s AR factorization, restricted to top-K candidates.

## 7) Will bidirectional vs left-to-right be a problem?

- **No, if you provide bidirectional soft targets** (FIM or suffix scoring). Then the student and teacher are aligned in conditioning.
- **If you use left-only targets**, the conditioning mismatch exists, but mixing KD with hard CE (and training the student on true bidirectional context) works in practice; the student learns to leverage right context while being softly biased by teacher’s left context.
- In SFT, the prompt provides strong left context; the right context within the response is partly emergent. Semi-autoregressive remasking during inference can further reduce mismatch.

## 8) Additional tips for code models

- Use higher temperature \(T\) (2–4) for KD on code to avoid over-peaked teacher targets.
- Consider top-K or top-p filtering before normalization when constructing \(q_T\) to cut tails that add compute but little signal.
- Mask placement: emphasize identifiers, literals, and syntax tokens to amplify structural learning; optionally weight these positions higher in KD.
- Validate with exact-match style metrics (HumanEval/MBPP-like) and LLaDA-style conditional likelihood estimates with the low-variance masking scheme.

## 9) Evaluation alignment (likelihood and generation)

- For conditional likelihood (multiple choice), use the equivalent form with masking exactly \(l\) tokens; 128 Monte Carlo samples are typically stable for metrics requiring multiple tokens.
- For generation tasks, match LLaDA inference hyperparameters (answer length, steps, block length, remasking strategy). Tune steps-to-length ratio: more steps ≈ better quality until saturation.

## 10) Minimal loss change summary

Replace the masked CE target at masked positions by a convex combination:
- Hard CE on ground-truth token (as in LLaDA).
- Forward-KL to teacher’s bidirectional soft target distribution at a subset of masked positions:
\[
\underbrace{-\log p_\theta(x_i \mid x_t)}_{\text{hard CE}}
\quad \leadsto \quad
(1-\lambda)\,\big(-\log p_\theta(x_i \mid x_t)\big)
\;+\;
\lambda\,T^2\,\mathrm{KL}\!\left(q_T(\cdot \mid \text{left},\text{right})\;\Vert\;p_\theta^T(\cdot \mid x_t)\right)
\]
where \(q_T\) is obtained via FIM or suffix scoring (exact for a single masked token), or approximated by left-only if necessary.
- If your teacher has FIM, use it; otherwise, suffix scoring with top-K is the most faithful way to obtain bidirectional soft targets.
- Prefer sharing the tokenizer between teacher and student.

- Implemented: defined a cross-architecture KD loss; showed how to get bidirectional targets from a left-to-right teacher; provided pseudocode and practical training settings.
