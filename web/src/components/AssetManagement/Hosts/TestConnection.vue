<script setup>
import { ref } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';

const handleTestConnection = async (hostId, ipAddress, port, credentialId) => {
  try {
    const response = await axios.post('/api/hosts/test-connection/', {
      host_id: hostId,
      ip_address: ipAddress,
      port: port,
      credential_id: credentialId,
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      },
    });

    if (response.data.status === 0) {
      message.success('连接成功');
    } else {
      message.error(`连接失败: ${response.data.error}`);
    }
  } catch (error) {
    message.error('测试连接失败');
  }
};
</script>
