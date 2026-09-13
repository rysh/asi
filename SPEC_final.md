# SiC26 Deck — 新構成仕様 (sic26_presentation_final.md 準拠)

## 0. 位置づけ
`sic26_presentation_final.md` を唯一の内容ソースとする。旧 `sic26_presentation_structure.md`
準拠の18枚デッキ (slides/content/part1_definition.py, part2_vision.py) は破棄し、
新構成で全面的に書き換える。描画基盤 (geometry / theme / render / shapes / validate) は再利用する。

## 1. 全体構成 (24枚)

| # | セクション | タイトル | 形式 | 秒 |
|---|---|---|---|---|
| 1 | — | Redefining Artificial Superintelligence | TitleBlock | 20 |
| 2 | — | Where This Talk Goes (Agenda) | TwoColumn | 25 |
| 3 | — | About the Author | TwoColumn (dense, wide) | 25 |
| 3 | 1 | The Mystification of Genius | Bullets | 55 |
| 4 | 1 | Genius as Outlier | Bullets | 65 |
| 5 | 1 | A Goal That Does Not Exist | Bullets | 40 |
| 6 | 2 | Bostrom: Achieved Conditions and a Metaphor | Bullets | 55 |
| 7 | 2 | Legg & Hutter: A Definition That Cannot Be Computed | Bullets | 35 |
| 8 | 2 | Chollet: Calling Infant Learning Intelligence | Bullets | 45 |
| 9 | 2 | Goertzel: AGI Does Not Scale Into ASI | Bullets | 60 |
| 10 | 3 | Calibrating the Definition | Bullets | 55 |
| 11 | 3 | The Four Conditions | Diagram FOUR_CONDITIONS | 60 |
| 12 | 3 | No Abduction, No Creativity | Bullets | 50 |
| 13 | 3 | Scaling Is Dead | Bullets | 50 |
| 14 | 3 | Two Challenges, Solved Separately | Image AXES + lead | 55 |
| 15 | 4 | Speed and Accuracy Are Only Prerequisites | Bullets | 45 |
| 16 | 4 | ASI = Continuous Novel Discovery | Image TRIANGLE + lead | 40 |
| 17 | 5 | General Does Not Mean Universal | Bullets | 40 |
| 18 | 5 | What Does General Mean? | Bullets | 40 |
| 19 | 5 | The Distinction Between AGI and ASI | Bullets | 35 |
| 20 | 6 | LLMs Cannot Judge Their Own Discoveries | Bullets | 45 |
| 21 | 6 | The Error of "In the Beginning Was the Word" | Bullets | 55 |
| 22 | 6 | What Advances Intelligence | Bullets | 60 |
| 23 | 6 | Is Truth Found or Made? | Bullets | 65 |
| 24 | 6 | Going Outside Language | Bullets | 45 |
| 25 | 7 | One Possible Design | Image LOOP6 + lead | 50 |
| 26 | 7 | Experiment as a Service | Image ECOSYSTEM + lead | 45 |
| 27 | 7 | Accelerating Novel Discovery | Image COMPARE + lead | 40 |
| 28 | — | Thank You / Questions | ContactBlock | 30 |

合計 29枚 / 1200秒 (20:00)。上表の # は分割前の番号であり、実装は 1〜29 の連番。秒配分は合計が正確に 1200 になるよう調整する。

## 2. 内容規約 (MD の Principle より)
- **MD の本文は一字一句そのまま使う。要約・言い換え・省略・語調の調整はしない。**
  MD が `=` `→` や括弧書きで書いている箇所もそのまま保持する
  (例:「Skill-acquisition efficiency = intelligence」)。
- スライドは話者なしで読めること。孤立した単語の箇条書きは禁止。
- hedging / academic disclaimer は書かない。立場は直接述べる。
- 全て英語。
- 旧デッキの `caveat` 機構は、MD が明示的に注記している箇所のみ使用する。
  MD にない留保を勝手に追加しない (旧デッキは hedging を多く含んでいたが、
  新 Principle はそれを禁じている)。

## 3. 参考文献 (refs.py)
MD 本文の footnote と About the Author の DOI をすべて登録する。
- footnote に現れる論文: processing_speed, who_are_we, intention_without_causation,
  conservation, lost_abduction, control_imposs, gen_contradiction, mishima
- About the Author: 出版済3件 + 査読中10件
DOI 文字列はコード中 refs.py にのみ書く (既存規約を維持)。
本タスクで Zenodo から取得したフルタイトルを正とする。

### 3.1 今回 DOI から取得・更新したフルタイトル
| DOI | フルタイトル |
|---|---|
| 19942221 | Brain Interoception: The Missing Organ on the Interoceptive Map |
| 21319707 | Emergence Without the Dichotomy |
| 21759090 | From Fugitive Cash to Non-Fugitive Provisioning: The Mundellian Trilemma, External Debt Feedback, and the Design Space of Post-Employment Redistribution |
| 18074645 | Dynamic Emergence: A Unified Theory Based on the Stuart-Landau Equation |
| 20005937 | Lost Abduction and Epistemic Barriers: Toward a Completion Model of Science Communication |
| 18017028 | From Instability to Active Inference: A Unified Mathematical Framework for Biological Self-Organization across Scales |
| 20642039 | When the Manifold Collapses: A Geometric Theory of Constraint Conflict in Large Language Models |

タイトルは一切省略しない。出版リスト・footnote ともにフルタイトルを用いる。
出版リストの行形式は MD に合わせて `Venue — Full Title (doi.org/DOI)`。
in press は `(in press; preprint doi.org/...)`、PubMed ID があれば末尾に付す。
13 件をフルタイトル＋DOI で載せると 1 枚に収まらないため、
About the Author を「Published (3)」と「Under review (10)」の 2 枚に分割する。
省略ではなく分割で対応すること (タイトルそのものが内容であるため)。

## 4. 画像 (5枚)
MD が指定する 5 箇所は、ユーザ提供の画像ファイルを貼り込む。

| スライド | MD 内 ID | 内容 | 想定キー |
|---|---|---|---|
| 14 | F08FC9CF | Distinct Capability Axes (2軸独立スケーリング) | `axes` |
| 16 | 4491494F | Reality / Novel Discovery / Updated Knowledge の三角ループ | `triangle` |
| 25 | A5305172 | 6-step Autonomous Research Agent loop | `loop6` |
| 26 | 7BC6B680 | Many Specialized Agents / One Growing Intelligence | `ecosystem` |
| 27 | C5041EF4 | Humanity vs ASI サイクル速度比較 | `compare` |

### 4.1 モデル拡張
```python
@dataclass(frozen=True)
class Image:
    key: str                      # assets/ 配下のファイルを引くキー
    caption: str | None = None
    lead: tuple[Bullet, ...] = ()
```
- 画像は `assets/<key>.png` から読む。
- `render.py` が `add_picture` で配置。アスペクト比を保ったまま、
  lead 消費後の残り領域 (body_rect) に収まる最大サイズで中央寄せ。
- `validate.py` は「ファイルが存在すること」「実寸から算出した配置矩形が
  スライド内に収まること」を検査する。ファイル欠落はビルド失敗とする
  (build.py の「検査を全て通らなければ何も書かない」方針に従う)。

## 5. テスト (tests/)
仕様に従う。実装ではなく本仕様と MD に照らして検証する。
- 構成: 枚数、番号の連続性、全スライドにタイトル、合計 1200 秒
- 参照: 全 ref id が REFS に登録済み、DOI 文字列が MD と一致
- 内容: 各セクションの中心主張がデッキ本文に現れる (MD からの抜粋文字列で照合)
- 禁止: MD の Principle に反する hedging 語彙 ("perhaps", "arguably", "may suggest" 等)
  が本文に出現しないこと
- 可読性: `check_all(SLIDES) == ()`
- 画像: 5 キーすべてが assets に存在し、配置がスライド内に収まる

## 6. 図版の実配置 (提供済み)
ユーザ提供の 5 点を assets/ に配置済み。MD の `uploaded file` ID と一致を確認した。

| キー | 元ファイル ID | 画素 | 備考 |
|---|---|---|---|
| axes | F08FC9CF | 1672x941 | ダーク背景 |
| triangle | 4491494F | 1672x941 | ダーク背景 |
| loop6 | A5305172 | 1672x941 | ダーク背景 |
| ecosystem | 7BC6B680 | 1536x1024 | **ライト背景**。他4点と地色が異なる |
| compare | C5041EF4 | 1672x941 | ダーク背景 |

## 7. 実装上の決定 (仕様からの確定事項)
- 四条件の並びは MD 3-2 に従い Speed / Collective / Scientific Creativity /
  General Wisdom とする。旧デッキは 3 番目と 4 番目が逆だったため修正した。
  スライド18 が「Condition 4 — general wisdom」と参照するのはこの並びによる。
- 閾値の破線は achieved と frontier の間の 1 本のみ。旧デッキの AGI/ASI 2 本は
  新 MD が条件に AGI/ASI レベルを割り当てていないため廃止した。
- Bullets 本文は上寄せではなく上下中央寄せで描画する。短いスライドで
  下半分が空くのを避けるため。図の上に置く lead は従来どおり上寄せ。
- 箇条書きの検査は語数の下限 (4語) のみとする。MD の文は終端ピリオドを持たず、
  「Incomputable by the authors' own admission」のように連結語を欠く主張もあるため、
  構文的な判定は行わない。この検査が防ぐのは 1〜2 語の断片だけである。
## 8. 可読性の設計 (レイアウト規則)
- **本文はスライドごとに自動スケールする** (`validate.fitted_scale`)。
  基準ランプ (L0 19pt / L1 16pt) に対し、本文が本文領域の
  `target_fill` (0.92) を超えない範囲で最大の倍率を二分探索で求める。
  文字を大きくすると行が増えて折り返すため、割り算ではなく探索が必要。
  - 上限 `max_body_pt` = 26pt。タイトル (30pt) より小さく保つ。
    本文が見出しより大きいと階層が反転して誤りに見えるため。
  - 下限 `min_body_pt` = 14pt。倍率は 1.0 以上のみ (拡大専用)。
    縮小を許すとオーバーフロー検査を骨抜きにするため。
  - 結果: 本文は 21〜26pt に分布する (従来は一律 19pt)。
- Bullets 本文は上寄せ。中央寄せにするとタイトルとの間が空き、
  本文が見出しから切り離されて見えるため。
- 図のキャプションは `figure_caption_pt` (15pt) で描く。
  キャプションは注記ではなく論の一部であり、10pt の caveat とは区別する。
- **強調 (太字＋白) は各スライドの中心主張のみ。** 全体の 3 割程度に留める。
  半数近くを強調すると強調が信号として機能しなくなる。
- 自己紹介は左右 2 段組みで 1 枚。13 件を標準余白の 2 段に入れると 11pt が
  必要で下限を割るため、この 1 枚のみ `wide=True` で全面レイアウトを使う
  (左右余白 0.38in / 段間 0.2in、`geometry.wide_body_rect`)。
  文献スライドは後方から読むものではなく走査するものなので、
  本文余白より広く取ってよい。
- 出版リストの DOI は Zenodo 共通接頭辞を省いて `zenodo.NNNNNNNN` と書く。
  13 件が並ぶ画面で `10.5281/zenodo.` の 15 文字は情報を持たないため。
  **footnote は従来どおり解決可能な `doi.org/10.5281/zenodo.NNNNNNNN` 形式**。
  Zenodo 以外の DOI (Springer / Elsevier) は短縮せず `doi.org/` 形式のまま。
- 前置き注記 (Preprints on Zenodo ほか) はタイトルスライドの meta に置く。
- 著者の肩書き行は `caveat_prominent=True` でスライド下部の全幅帯に
  19pt / accent (白) / 太字で置く。通常の caveat (10pt / muted / 斜体) は
  免責のための小書きだが、この行は内容であるため区別する。
  帯の開始位置 `CAVEAT_PROMINENT_TOP_IN` はレンダリング実測に基づく。
  幅推定器 (`AVG_CHAR_EM = 0.575`) は保守的で、長いタイトルが並ぶ段では
  実測より約 15% 高く見積もるため、推定値では「余白なし」と判定されてしまう。
  推定器自体は右段では実測比 0.99 と正確であり、系統誤差ではないので
  定数は変更しない。
- **目次スライド (2 枚目) を置く。** 7 セクションを前半 (問いの側の問題) /
  後半 (フロンティアが要求するもの) に分け、各節に 1 行の説明を付す。
