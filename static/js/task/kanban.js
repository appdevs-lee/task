document.addEventListener('DOMContentLoaded', function() {
    // DOM 요소 참조
    const taskCards = document.querySelectorAll('.task-card');
    const columns = document.querySelectorAll('.kanban-column');
    const modal = document.getElementById('task-detail-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const closeModal = document.querySelector('.close');
    const editTaskBtn = document.getElementById('edit-task-btn');
    const deleteTaskBtn = document.getElementById('delete-task-btn');
    
    // 드래그 앤 드롭 구현
    let draggedItem = null;
    
    // 각 작업 카드에 이벤트 리스너 추가
    taskCards.forEach(card => {
        // 드래그 시작 시
        card.addEventListener('dragstart', function(e) {
            draggedItem = this;
            setTimeout(() => {
                this.classList.add('dragging');
            }, 0);
        });
        
        // 드래그 종료 시
        card.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            draggedItem = null;
        });
        
        // 작업 카드 클릭 시 간단한 모달 표시
        card.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = this.getAttribute('data-task-id');
            showSimpleTaskDetail(taskId, this);
        });
    });
    
    // 칸반 컬럼에 드래그 이벤트 리스너 추가
    columns.forEach(column => {
        // 드래그 오버 시 (필수: 기본 동작 방지)
        column.addEventListener('dragover', function(e) {
            e.preventDefault();
            const afterElement = getDragAfterElement(this, e.clientY);
            const columnBody = this.querySelector('.column-body');
            
            if (afterElement) {
                columnBody.insertBefore(draggedItem, afterElement);
            } else {
                columnBody.appendChild(draggedItem);
            }
        });
        
        // 드롭 시
        column.addEventListener('drop', function(e) {
            e.preventDefault();
            const newStatus = this.getAttribute('data-status');
            const taskId = draggedItem.getAttribute('data-task-id');
            
            // API 호출로 작업 상태 업데이트
            updateTaskStatus(taskId, newStatus);
            
            // 작업 수 업데이트
            updateTaskCount();
        });
    });
    
    // 모달 닫기 버튼
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // 모달 외부 클릭 시 닫기
    window.addEventListener('click', function(e) {
        if (e.target == modal) {
            modal.style.display = 'none';
        }
    });
    
    // ESC 키로 모달 닫기
    window.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            modal.style.display = 'none';
        }
    });
    
    /**
     * 드래그 후 요소 위치 계산 헬퍼 함수
     */
    function getDragAfterElement(column, y) {
        const cards = [...column.querySelectorAll('.task-card:not(.dragging)')];
        
        return cards.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
    
    /**
     * 작업 상태 업데이트 API 호출
     */
    function updateTaskStatus(taskId, newStatus) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/task/update-status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                task_id: taskId,
                status: newStatus
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('상태 업데이트 실패:', data.error);
                // 필요 시 사용자에게 오류 알림
            }
        })
        .catch(error => {
            console.error('API 오류:', error);
        });
    }
    
    /**
     * 각 컬럼의 작업 수 업데이트
     */
    function updateTaskCount() {
        columns.forEach(column => {
            const count = column.querySelectorAll('.task-card').length;
            column.querySelector('.task-count').textContent = count;
        });
    }
    
    /**
     * 작업 카드에서 직접 정보를 가져와 모달에 표시 (API 호출 대체)
     */
    function showSimpleTaskDetail(taskId, cardElement) {
        try {
            // 카드에서 직접 정보 가져오기
            const title = cardElement.querySelector('.task-header h3').textContent;
            const description = cardElement.querySelector('.task-description') ? 
                                cardElement.querySelector('.task-description').textContent : '설명 없음';
            
            // 담당자 정보 가져오기
            let assignedTo = '없음';
            let dueDate = '없음';
            
            const metaItems = cardElement.querySelectorAll('.task-meta p');
            metaItems.forEach(item => {
                if (item.textContent.includes('담당:')) {
                    assignedTo = item.textContent.replace('담당:', '').trim();
                }
                if (item.textContent.includes('마감일:')) {
                    dueDate = item.textContent.replace('마감일:', '').trim();
                }
            });
            
            // 우선순위 가져오기
            let priority = '0';
            const priorityBadge = cardElement.querySelector('.priority-badge');
            if (priorityBadge) {
                priority = priorityBadge.textContent.replace('우선순위:', '').trim();
            }
            
            // 상태 확인
            let status = '진행 전';
            const column = cardElement.closest('.kanban-column');
            if (column) {
                const columnId = column.getAttribute('id');
                if (columnId === 'in-progress-column') status = '진행 중';
                else if (columnId === 'done-column') status = '완료';
            }
            
            // 모달 내용 설정
            modalTitle.textContent = title;
            modalBody.innerHTML = `
                <div class="task-info">
                    <p><strong>상태:</strong> ${status}</p>
                    <p><strong>우선순위:</strong> ${priority}</p>
                    <p><strong>담당자:</strong> ${assignedTo}</p>
                    <p><strong>마감일:</strong> ${dueDate}</p>
                </div>
                <div class="task-description">
                    <h2>설명</h2>
                    <div class="description-content">
                        <p>${description}</p>
                    </div>
                </div>
            `;
            
            // 버튼 URL 설정
            editTaskBtn.href = `/task/${taskId}/update/`;
            deleteTaskBtn.href = `/task/${taskId}/delete/`;
            
            // 모달 표시
            modal.style.display = 'block';
            
        } catch (error) {
            console.error('카드 정보 추출 오류:', error);
            
            // 오류 발생 시 기본 정보만 표시
            modalTitle.textContent = `업무 ${taskId}`;
            modalBody.innerHTML = `
                <p>업무 정보를 표시할 수 없습니다.</p>
                <p>상세 정보는 아래 링크를 통해 확인하세요.</p>
            `;
            
            editTaskBtn.href = `/task/${taskId}/update/`;
            deleteTaskBtn.href = `/task/${taskId}/delete/`;
            
            modal.style.display = 'block';
        }
    }
});