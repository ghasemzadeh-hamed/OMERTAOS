use std::collections::VecDeque;
use std::sync::Arc;

use parking_lot::Mutex;

use crate::contracts::TaskEnvelope;

pub trait TaskQueue: Send + Sync {
    fn push(&self, task: TaskEnvelope);
    fn pop(&self) -> Option<TaskEnvelope>;
}

#[derive(Clone, Default)]
pub struct InMemoryTaskQueue {
    queue: Arc<Mutex<VecDeque<TaskEnvelope>>>,
}

impl TaskQueue for InMemoryTaskQueue {
    fn push(&self, task: TaskEnvelope) {
        let mut guard = self.queue.lock();
        guard.push_back(task);
    }

    fn pop(&self) -> Option<TaskEnvelope> {
        let mut guard = self.queue.lock();
        guard.pop_front()
    }
}
