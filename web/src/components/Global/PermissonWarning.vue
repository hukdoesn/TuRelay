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
</script>