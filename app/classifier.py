import re


LABELS = [
    "就活/要確認",
    "就活/要返信",
    "就活/面接",
    "就活/説明会",
    "就活/ES",
    "就活/適性検査",
    "就活/合否",
    "就活/広報",
    "就活/その他",
]


CATEGORY_RULES = {
    "就活/面接": [r"面接", r"面談", r"日程調整", r"一次面接", r"最終面接"],
    "就活/ES": [r"\bES\b", r"エントリーシート", r"提出", r"応募書類"],
    "就活/適性検査": [r"適性検査", r"\bSPI\b", r"受検", r"WEBテスト"],
    "就活/説明会": [r"説明会", r"セミナー", r"会社説明", r"インターン"],
    "就活/合否": [r"合格", r"通過", r"不合格", r"見送り", r"お祈り"],
    "就活/要返信": [r"返信ください", r"ご返信", r"ご回答", r"ご確認ください", r"要返信"],
    "就活/広報": [r"メルマガ", r"ニュースレター", r"お知らせ", r"自動配信", r"キャンペーン"],
}

JOB_RELATED_PATTERNS = [
    r"採用",
    r"就活",
    r"面接",
    r"説明会",
    r"エントリー",
    r"\bES\b",
    r"適性検査",
    r"\bSPI\b",
    r"選考",
]

SENDER_PRIORITY_PATTERNS = [
    r"@mypage\.",
    r"recruit",
    r"jinji",
    r"saiyo",
    r"\bhr\b",
]


def _match_any(patterns, text):
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def is_job_related(sender, subject, body):
    combined = " ".join(filter(None, [sender, subject, body]))
    return _match_any(JOB_RELATED_PATTERNS, combined) or _match_any(
        SENDER_PRIORITY_PATTERNS, sender or ""
    )


def classify_email(sender, subject, body):
    combined = " ".join(filter(None, [subject, body, sender]))

    for category in [
        "就活/面接",
        "就活/ES",
        "就活/適性検査",
        "就活/説明会",
        "就活/合否",
        "就活/要返信",
        "就活/広報",
    ]:
        if _match_any(CATEGORY_RULES[category], combined):
            return category

    if "noreply" in (sender or "").lower():
        return "就活/広報"

    if is_job_related(sender, subject, body):
        return "就活/要確認"

    return "就活/その他"
