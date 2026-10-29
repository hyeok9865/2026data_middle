import json

d = json.load(open("deck/data.json", encoding="utf-8"))
for m in d["models"]:
    k = m["metrics"]
    print(f"{m['name']:<14} 만족도={k['satisfaction']} 언급={k['mentions']} 의견={k['opinion']} "
          f"소스={k['sources']} 부정문={k['neg_ratio']}% 긍정어={m['keywords']['pos']} 부정어={m['keywords']['neg']}")
