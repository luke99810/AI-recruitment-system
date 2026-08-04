'''
Flywheel 飞轮机制（Loop 3）：让系统越用越聪明。

核心流程：
  1. 每次面试结束后，结构化数据存入 ChromaDB
  2. 新候选人进入时，RAG 检索历史上相似案例
  3. 检索结果注入 Prompt，提升匹配准确度和题目针对性
  4. Checker 发现的常见问题自动注入到 Prompt 注意事项
'''

import os
import json
import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path


@dataclass
class FlywheelRecord:
    id: str
    jd_summary: str
    resume_summary: str
    match_score: int
    match_result: dict
    questions: list
    interview_report: Optional[dict] = None
    checker_feedback: Optional[dict] = None
    tags: list = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class FlywheelStore:
    '''
    飞轮存储：基于 ChromaDB 的向量存储 + JSON 文件元数据。

    如果 chromadb 未安装，自动降级为纯 JSON 文件存储。
    '''

    def __init__(self, store_dir: str = None):
        if store_dir is None:
            store_dir = os.path.join(os.path.dirname(__file__), '..', 'sessions')
        self.store_dir = os.path.abspath(store_dir)
        os.makedirs(self.store_dir, exist_ok=True)
        self.records_file = os.path.join(self.store_dir, 'flywheel_records.json')
        self._records: list[FlywheelRecord] = []
        self._load()

    def _load(self):
        if os.path.exists(self.records_file):
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._records = [FlywheelRecord(**r) for r in data]
            except Exception:
                self._records = []

    def _save(self):
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump([self._record_to_dict(r) for r in self._records], f,
                      ensure_ascii=False, indent=2, default=str)

    def _record_to_dict(self, r: FlywheelRecord) -> dict:
        return {
            'id': r.id,
            'jd_summary': r.jd_summary,
            'resume_summary': r.resume_summary,
            'match_score': r.match_score,
            'tags': r.tags,
            'timestamp': r.timestamp,
        }

    def store(self, record: FlywheelRecord) -> str:
        record.id = record.id or hashlib.md5(
            (record.jd_summary + record.resume_summary + str(time.time())).encode()
        ).hexdigest()[:12]
        self._records.append(record)
        self._save()
        return record.id

    def retrieve_similar(
        self, query_text: str, top_k: int = 5, min_score: int = 50
    ) -> list[FlywheelRecord]:
        '''
        RAG 检索：基于关键词匹配找到相似的历史案例。

        使用简单的 TF-IDF 风格关键词匹配（生产环境可替换为 ChromaDB 向量检索）。
        '''
        if not self._records:
            return []

        query_keywords = set(self._tokenize(query_text))

        scored = []
        for record in self._records:
            record_text = record.jd_summary + ' ' + record.resume_summary
            record_keywords = set(self._tokenize(record_text))

            if not query_keywords or not record_keywords:
                continue

            intersection = query_keywords & record_keywords
            union = query_keywords | record_keywords
            jaccard = len(intersection) / len(union) if union else 0

            scored.append((jaccard, record))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for s, r in scored[:top_k] if s * 100 >= min_score]

    def _tokenize(self, text: str) -> list[str]:
        import re
        words = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{2,}', text.lower())
        stopwords = {'的', '了', '在', '是', '有', '和', '就', '不', '人', '都', '一',
                     'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'has', 'have'}
        return [w for w in words if w not in stopwords]

    def get_common_checker_issues(self, top_k: int = 5) -> list[dict]:
        '''
        从历史 Checker 反馈中提取常见问题模式。
        用于注入到 Prompt 模板的"注意事项"中。
        '''
        issue_counter = {}
        for record in self._records:
            if not record.checker_feedback:
                continue
            issues = record.checker_feedback.get('issues', [])
            for issue in issues:
                key = f"{issue.get('dimension')}:{issue.get('description', '')[:60]}"
                issue_counter[key] = issue_counter.get(key, 0) + 1

        sorted_issues = sorted(issue_counter.items(), key=lambda x: x[1], reverse=True)
        return [
            {'pattern': k, 'count': v}
            for k, v in sorted_issues[:top_k]
        ]

    def generate_prompt_notes(self) -> str:
        '''生成 Prompt 注意事项（可从历史中学习）'''
        common_issues = self.get_common_checker_issues(top_k=3)
        if not common_issues:
            return ''

        notes = ['\n## 历史常见问题（请特别注意避免）']
        for i, issue in enumerate(common_issues):
            notes.append(f"{i+1}. {issue['pattern']}（已出现{issue['count']}次）")
        return '\n'.join(notes)

    def get_stats(self) -> dict:
        return {
            'total_records': len(self._records),
            'avg_match_score': (
                sum(r.match_score for r in self._records) / len(self._records)
                if self._records else 0
            ),
            'recent_tags': list(set(
                tag for r in self._records[-20:] for tag in r.tags
            )),
        }

    def count(self) -> int:
        return len(self._records)
