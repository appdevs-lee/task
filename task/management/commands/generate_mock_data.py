from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
import random
from datetime import timedelta

from task.models import (
    Task,
    TaskStatus,
)


class Command(BaseCommand):
    help = "가상 업무 데이터를 생성합니다 (로그인 없이 테스트용)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tasks",
            type=int,
            default=20,
            help="생성할 업무의 수",
        )

    def handle(self, *args, **options):
        num_tasks = options["tasks"]

        self.stdout.write(f"{num_tasks}개의 업무 데이터를 생성합니다...")

        # 기본 관리자 사용자 하나만 생성 또는 가져오기
        admin_user = self._get_or_create_admin_user()

        # 랜덤 업무 생성
        self._create_tasks(num_tasks, admin_user)

        self.stdout.write(self.style.SUCCESS("가상 데이터 생성 완료!"))

    def _get_or_create_admin_user(self):
        """기본 관리자 사용자 생성 또는 가져오기"""
        if User.objects.filter(username="admin").exists():
            return User.objects.get(username="admin")
        else:
            admin = User.objects.create_superuser(
                username="admin", email="admin@example.com", password="admin123"
            )
            self.stdout.write("관리자 계정 생성: admin / admin123")
            return admin

    @transaction.atomic
    def _create_tasks(self, num_tasks, user):
        """가상 업무 생성 (모든 업무는 같은 사용자가 생성하고 담당)"""
        # 업무 상태 배분 (진행 전: 50%, 진행 중: 30%, 완료: 20%)
        statuses = [
            TaskStatus.TODO,
            TaskStatus.TODO,
            TaskStatus.TODO,
            TaskStatus.TODO,
            TaskStatus.TODO,
            TaskStatus.IN_PROGRESS,
            TaskStatus.IN_PROGRESS,
            TaskStatus.IN_PROGRESS,
            TaskStatus.DONE,
            TaskStatus.DONE,
        ]

        # 가상 업무 제목 및 설명 데이터
        task_titles = [
            "웹사이트 디자인 검토",
            "로그인 페이지 구현",
            "데이터베이스 스키마 설계",
            "사용자 피드백 수집",
            "성능 최적화",
            "버그 수정",
            "보안 취약점 분석",
            "백업 시스템 구축",
            "사용자 매뉴얼 작성",
            "배포 자동화 구현",
            "단위 테스트 작성",
            "코드 리뷰",
            "API 문서화",
            "대시보드 기능 개발",
            "통계 차트 구현",
            "결제 시스템 연동",
            "SEO 최적화",
            "푸시 알림 기능 추가",
            "다국어 지원 구현",
            "모바일 반응형 대응",
        ]

        description_templates = [
            "{title}을(를) 위해 {action}이 필요합니다. {extra}",
            "{action}하여 {title}을(를) 완료해야 합니다. {extra}",
            "{title} 작업을 위한 {action}이 요구됩니다. {extra}",
            "{action} 후 {title} 결과물을 전달해주세요. {extra}",
            "{title}의 진행 상황을 {action}해주세요. {extra}",
        ]

        actions = [
            "요구사항 분석",
            "디자인 검토",
            "코드 작성",
            "테스트",
            "문서화",
            "회의 진행",
            "피드백 수집",
            "리서치",
            "리팩토링",
            "성능 측정",
        ]

        extras = [
            "가능한 빨리 완료해주세요.",
            "다음 주 회의 전까지 완료 필요합니다.",
            "관련 자료는 공유 드라이브에 있습니다.",
            "이전 작업 결과를 참고하세요.",
            "어려움이 있으면 즉시 알려주세요.",
            "타 부서와 협업이 필요합니다.",
            "높은 품질이 요구됩니다.",
            "예산 내에서 최적의 솔루션을 찾아주세요.",
            "사용자 경험을 최우선으로 고려해주세요.",
            "관련 팀원들과 미팅 후 진행해주세요.",
        ]

        # 현재 날짜 기준으로 날짜 범위 설정
        now = timezone.now()

        # 업무 생성
        created_tasks = []
        for i in range(num_tasks):
            # 제목 설정 (반복을 위해 인덱스 계산)
            title_idx = i % len(task_titles)
            title = f"{task_titles[title_idx]} {i+1}"

            # 설명 생성
            description_template = random.choice(description_templates)
            action = random.choice(actions)
            extra = random.choice(extras)
            description = description_template.format(
                title=task_titles[title_idx], action=action, extra=extra
            )

            # 날짜 설정
            created_days_ago = random.randint(0, 30)
            created_date = now - timedelta(days=created_days_ago)

            # 마감일 설정 (80%는 마감일 있음, 20%는 없음)
            due_date = None
            if random.random() < 0.8:
                due_days = random.randint(-10, 30)  # 일부는 이미 마감일 지남
                due_date = now + timedelta(days=due_days)

            # 상태 설정
            status = random.choice(statuses)

            # 우선순위 설정 (0-5)
            priority = random.randint(0, 5)

            # 업무 생성
            task = Task.objects.create(
                title=title,
                description=description,
                status=status,
                priority=priority,
                created_at=created_date,
                updated_at=created_date,
                due_date=due_date,
                assigned_to=user,  # 모든 업무는 같은 사용자가 담당
                created_by=user,  # 모든 업무는 같은 사용자가 생성
            )

            created_tasks.append(task)

        self.stdout.write(f"{len(created_tasks)}개의 업무 생성 완료")
        return created_tasks
