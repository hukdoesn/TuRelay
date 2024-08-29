<script>
import { Modal } from 'ant-design-vue';
import { h } from 'vue';

export const showPermissionWarning = () => {
  Modal.error({
    title: '权限提示',
    content: h('div', {}, [
      h('p', '只读用户禁止增加、删除、修改等操作。'),
    ]),
    onOk() {
      //   console.log('权限提示确认关闭');
    },
  });
};

// 权限检查函数
export const checkPermission = (callback) => {
  const token = localStorage.getItem('accessToken');
  if (!token) {
    showPermissionWarning();
    return;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1])); // 解码JWT的负载部分
    if (payload.is_read_only) {
      showPermissionWarning();  // 调用分离的权限提示函数
    } else {
      callback(); // 如果用户有权限，执行回调函数
    }
  } catch (error) {
    console.error('权限检查过程中发生错误:', error);
    showPermissionWarning();
  }
};
</script>