// Public practice questions only. No answer key or scoring data is shipped to the page.
const questions = [
  { text: "普通单选：1 + 1 等于多少？", options: ["1", "2", "3", "4"], type: "radio" },
  { text: "否定单选：以下哪个不是偶数？", options: ["2", "4", "3", "6"], type: "radio" },
  { text: "双重否定：以下哪项并非不正确？", options: ["2 + 2 = 4", "2 + 2 = 5", "2 + 2 = 6", "2 + 2 = 7"], type: "radio" },
  { text: "普通多选：选出所有偶数。", options: ["1", "2", "3", "4"], type: "checkbox" },
  { text: "判断：1 + 1 = 2。", options: ["正确", "错误"], type: "radio" },
  { text: "动态事实：测试数据库今天 UTC 的模拟结果数是多少？", options: ["1", "2", "3", "无法离线核验"], type: "radio" },
  { text: "绝对化：所有素数都是奇数吗？", options: ["是", "否"], type: "radio" },
  { text: "官方来源：Playwright MCP isolated profile 是否保存状态？", options: ["保存", "不保存"], type: "radio" },
  { text: "高校信息素养教育数据库路由：未配置真实数据库入口时，应如何处理检索题？", options: ["猜测入口", "直接按模型记忆作答", "标记 CONFIG_REQUIRED", "绕过认证"], type: "radio" },
  { text: "综合题：2 + 3 等于多少？", options: ["4", "5", "6", "7"], type: "radio" }
];

let index = 0;
const selections = questions.map(() => []);
let submitted = false;
const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const byId = (id) => document.getElementById(id);

function render() {
  const question = questions[index];
  byId("position").textContent = "第 " + (index + 1) + " / " + questions.length + " 题";
  byId("question").textContent = question.text;
  const form = byId("options");
  form.replaceChildren();
  question.options.forEach((option, number) => {
    const label = document.createElement("label");
    const input = document.createElement("input");
    input.type = question.type;
    input.name = "answer";
    input.value = letters[number];
    input.checked = selections[index].includes(letters[number]);
    label.append(input, document.createTextNode(" " + letters[number] + ". " + option));
    form.append(label);
  });
  byId("previous").disabled = index === 0;
  byId("next").disabled = index === questions.length - 1;
  byId("submit").hidden = index !== questions.length - 1;
  byId("status").textContent = submitted ? "Submitted (mock only)" : "";
}

byId("options").addEventListener("change", () => {
  selections[index] = Array.from(document.querySelectorAll('#options input:checked'), (input) => input.value);
});
byId("previous").addEventListener("click", () => { if (index > 0) { index -= 1; render(); } });
byId("next").addEventListener("click", () => { if (index < questions.length - 1) { index += 1; render(); } });
byId("submit").addEventListener("click", () => {
  submitted = true;
  byId("status").textContent = "Submitted (mock only)";
});
render();
