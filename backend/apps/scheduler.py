from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
import logging
import redis

logger = logging.getLogger('apscheduler')

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def check_redis_connection():
    """
    检查 Redis 连接是否成功
    """
    try:
        redis_client.ping()
        logger.info("Redis 连接成功")
        return True
    except redis.ConnectionError:
        logger.error("无法连接到 Redis")
        return False

# Define Scheduler
scheduler = BackgroundScheduler(
    jobstores={
        'default': RedisJobStore(host='localhost', port=6379, db=0),
    },
    executors={
        'default': ThreadPoolExecutor(20),
    },
    job_defaults={
        'coalesce': False,
        'max_instances': 1,
        'misfire_grace_time': 60
    },
    timezone=settings.TIME_ZONE,
)

def start_scheduler():
    """
    启动调度器
    """
    if check_redis_connection():
        if not scheduler.running:
            scheduler.start()
            logger.info("调度器已启动")
    else:
        raise RuntimeError("启动调度器失败：无法连接到 Redis")

def add_task(task_class, task_method, task_id, task_name, interval, *args):
    """
    添加定时任务
    """
    if not check_redis_connection():
        raise RuntimeError("添加定时任务失败：无法连接到 Redis")
    
    try:
        scheduler.add_job(
            task_method,
            trigger='interval',
            seconds=interval,
            id=task_id,
            name=task_name,
            args=args,
            replace_existing=True,
            misfire_grace_time=60
        )
        logger.info(f"已添加定时任务: {task_name} 每 {interval} 秒执行一次")
    except Exception as e:
        logger.error(f"添加定时任务失败: {str(e)}")

def remove_task(task_id):
    """
    移除定时任务
    :param task_id: 任务ID
    """
    job = scheduler.get_job(task_id)
    if job:
        scheduler.remove_job(task_id)
        logger.info(f"已移除定时任务: {task_id}")
    else:
        logger.warning(f"尝试删除不存在的任务: {task_id}")

def update_task(task_class, task_method, task_id, task_name, interval, *args):
    """
    更新定时任务
    :param task_class: 任务类
    :param task_method: 任务方法
    :param task_id: 任务ID
    :param task_name: 任务名称
    :param interval: 执行间隔（秒）
    :param args: 任务方法的参数
    """
    job = scheduler.get_job(task_id)
    
    if job:
        if job.next_run_time is None:  # 这表明工作已暂停
            job.resume()
            logger.info(f"已恢复定时任务: {task_id}")
        else:
            # 使用更新的间隔创建一个新的IntervalTrigger
            new_trigger = IntervalTrigger(seconds=interval)
            job.modify(trigger=new_trigger, args=args)
            logger.info(f"已更新定时任务: {task_id}, 执行间隔: {interval} 秒")
    else:
        add_task(task_class, task_method, task_id, task_name, interval, *args)

def pause_task(task_id):
    """
    暂停定时任务
    :param task_id: 任务ID
    """
    job = scheduler.get_job(task_id)
    if job:
        job.pause()
        logger.info(f"已暂停定时任务: {task_id}")
    else:
        logger.warning(f"尝试暂停不存在的任务: {task_id}")
