# Relationship Taxonomy — 关系类型、深度边界、连边规则

## 边类型（graph_store.py 的 `--type`）

`graph_store.py` 的边是**有向**的，三种类型：

| type | 方向语义（src → dst） | 渲染 |
|---|---|---|
| `advisor` | src 是 dst 的导师（mentor → mentee） | 红色实线箭头 |
| `student` | src 是 dst 的学生（mentee → mentor） | 绿色实线箭头 |
| `collaborator` | 知名直接合作者（无方向意义，存 src→dst） | 灰色虚线 |
| inferred 边 | 任意类型但未证实 | 灰点线，标"未证实" |

**脚本已自动规范化**：师承一律折叠成 `advisor`（导师→学生）。你传 `--type student a b`
（a 是 b 的学生）会被自动转成 `advisor b a`；同一对师生即使从两个方向、两个节点的
`relations` 各登记一次，`detect-connections --apply` 也只落 **一条** advisor 边
（iter-1 的"advisor + 反向 student 重复边"bug 已修）。所以你不必纠结方向，照实填
`relations.advisors`（谁指导了我）/ `relations.students`（我指导了谁）即可。
`collaborator` 无向、按节点对去重，仅用于学术知名的直接合作者。

## 深度边界（用户已拍板）

以被查学者 P 为中心：

- **导师方向：上溯 1 跳** —— 只画 P 的直接博士/博后导师。**不**再画导师的导师。
- **学生方向：下溯 2 跳** —— P 的直接博士生（子），以及这些学生各自的博士生（孙）。
  **不**再往下第 3 代。
- **合作者：仅直接且知名** —— P 的高频共同作者中本身学术知名者。不扩展合作者的合作者。

"知名"的判断要有依据（有 Wikipedia 词条 / 重大奖项 / 讲席 / 高引），并能给来源；
否则不单独建节点（避免图被无名节点淹没）。徒孙一代同理：优先画有职位/有据可查者。

## 一条边算不算"成立"

只有当你有**明确来源**说明二人确为师生/合作关系时，才用 `add-edge --source <URL>`
或 `detect-connections --apply`（只落有源边）建为**实边**。

不要把下列当实边：
- "同一所大学/同一公司" → 顶多 inferred 弱关联候选，必须另查到合作来源才连实边。
- "都研究深度学习" → 不是关系，别连。
- "论文里互相引用" → 引用 ≠ 师承/合作，除非来源明确说明合作关系。

## 自动连边怎么发生（核心机制）

`upsert-node` 时把 Phase 1 查到的关系人填进节点的 `relations`
（`advisors/students/collaborators`，每条带 `source`）。
之后 `detect-connections --node <id>` 会：

1. 看**本节点**声明的关系人里，有没有已在图中的节点 → 提议带原始 source 的边。
2. 看**其他节点**声明的关系人里，有没有指向本节点的 → 同样提议。
3. `--apply` 只自动落其中**有 source 的**；inferred/无源仅列出供你判断。

所以即便先问 A 时 B 还不在图里，等后来问 B，`detect-connections --node <B>`
也能凭 A 当初登记的 source 把 A–B 连起来。**因此 `relations` 里务必带 source，别图省事只写名字。**

## 命名一致性

同一个人不同写法（"李飞飞" vs "Fei-Fei Li"、有无中间名）会导致连不上。
- 建节点时把已知别名都放进 `aliases`（脚本按规范化姓名 + 别名匹配）。
- `relations` 里写关系人时，尽量用其最常见英文全名，并在 `note` 里附中文名，
  方便日后该人被正式建节点时仍能匹配上。
