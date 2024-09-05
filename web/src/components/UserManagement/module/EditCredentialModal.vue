<!-- EditCredentialModal.vue -->
<template>
    <!-- 编辑凭据的模态框 -->
    <a-modal v-model:open="isVisible" title="编辑凭据" @ok="handleOk" @cancel="handleCancel">
        <a-form 
            :model="form" 
            :rules="rules" 
            ref="formRef"
            layout="vertical"
        >
            <!-- 凭据名称输入框 -->
            <a-form-item label="名称" name="name" :rules="rules.name">
                <a-input v-model:value="form.name" placeholder="请输入名称" />
            </a-form-item>
            
            <!-- 凭据类型选择框 -->
            <a-form-item label="类型" name="type" :rules="rules.type">
                <a-radio-group v-model:value="form.type">
                    <a-radio value="密码">密码</a-radio>
                    <a-radio value="密钥">密钥</a-radio>
                    <a-radio value="AccessKey">AccessKey</a-radio>
                </a-radio-group>
            </a-form-item>

            <!-- 根据选择的类型显示不同的表单项 -->
            <template v-if="form.type === '密码'">
                <a-form-item label="账户" name="account" :rules="rules.account">
                    <a-input v-model:value="form.account" placeholder="请输入账户" />
                </a-form-item>
                <a-form-item label="密码" name="password" :rules="rules.password">
                    <a-input type="password" v-model:value="form.password" placeholder="请输入新密码" />
                </a-form-item>
            </template>
            
            <template v-if="form.type === '密钥'">
                <a-form-item label="账户" name="account" :rules="rules.account">
                    <a-input v-model:value="form.account" placeholder="请输入账户" />
                </a-form-item>
                <a-form-item label="密钥" name="key" style="margin-bottom: -15px;">
                    <a-textarea v-model:value="form.key" placeholder="请输入密钥"/>
                </a-form-item>
                <a-form-item>
                    <!-- 添加上传文件按钮 -->
                    <a-upload :before-upload="handleFileUpload" :show-upload-list="false">
                        <a-button type="dashed">上传文件</a-button>
                    </a-upload>
                </a-form-item>
                <a-form-item label="密钥密码" name="key_password" :rules="rules.key_password">
                    <a-input type="password" v-model:value="form.key_password" placeholder="请输入新密钥密码" />
                </a-form-item>
            </template>
            
            <template v-if="form.type === 'AccessKey'">
                <a-form-item label="Key ID" name="KeyId" :rules="rules.KeyId">
                    <a-input v-model:value="form.KeyId" placeholder="请输入Key ID" />
                </a-form-item>
                <a-form-item label="Key Secret" name="KeySecret" :rules="rules.KeySecret">
                    <a-input v-model:value="form.KeySecret" placeholder="请输入新Key Secret" />
                </a-form-item>
            </template>
            
            <!-- 备注输入框 -->
            <a-form-item label="备注" name="notes">
                <a-textarea v-model:value="form.notes" placeholder="请输入备注" />
            </a-form-item>
        </a-form>
    </a-modal>
</template>

<script setup>
// 引入必要的依赖
import { ref, reactive, defineExpose, defineEmits } from 'vue';
import { message } from 'ant-design-vue'
import axios from 'axios'
import { showPermissionWarning, checkPermission } from '@/components/Global/PermissonWarning.vue'

// 定义 emit 事件
const emit = defineEmits(['refresh']);

// 模态框的可见性状态
const isVisible = ref(false)

// 表单引用，用于表单验证和重置
const formRef = ref(null)

// 表单数据，用于存储用户输入的数据
const form = reactive({
    id: null,          // 凭据ID
    name: '',          // 凭据名称
    type: '密码',      // 凭据类型，默认值为'密码'
    account: '',       // 凭据账户
    password: '',      // 凭据密码
    key: '',           // 密钥
    key_password: '',  // 密钥密码
    KeyId: '',         // Key ID
    KeySecret: '',     // Key Secret
    notes: ''          // 备注
})

// 表单验证规则，用于验证用户输入的合法性
const rules = {
    name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
    type: [{ required: true, message: '请选择类型', trigger: 'change' }],
    account: [
        { required: true, message: '请输入账户', trigger: 'blur' },
        { pattern: /^[a-zA-Z]+$/, message: '账户名只能包含英文', trigger: 'blur' },
    ],
    password: [{ required: false, message: '请输入新密码', trigger: 'blur' }],
    key: [{ required: false, message: '请输入新密钥', trigger: 'blur' }],
    key_password: [{ required: false, message: '请输入新密钥密码', trigger: 'blur' }],
    KeyId: [{ required: true, message: '请输入Key ID', trigger: 'blur' }],
    KeySecret: [{ required: false, message: '请输入新Key Secret', trigger: 'blur' }],
}

// 重置表单内容的函数
const resetForm = () => {
    form.id = null
    form.name = ''
    form.type = '密码'
    form.account = ''
    form.password = ''
    form.key = ''
    form.key_password = ''
    form.KeyId = ''
    form.KeySecret = ''
    form.notes = ''
}

// 处理文件上传
const handleFileUpload = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
        form.key = e.target.result; // 将文件内容设置到密钥字段中
    };
    reader.readAsText(file);
    return false; // 阻止自动上传
};

// 处理模态框的确定按钮点击事件
const handleOk = () => {
    checkPermission(() => {
        // 验证表单数据
        formRef.value.validate().then(async () => {
            try {
                // 从localStorage获取JWT Token
                const token = localStorage.getItem('accessToken')
                // 发送PUT请求更新凭据
                await axios.put(`/api/credentials/${form.id}/update/`, form, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                })
                // 显示成功消息
                message.success('凭据更新成功')
                // 关闭模态框
                isVisible.value = false
                // 重置表单
                resetForm()
                // 通知父组件刷新凭据列表
                emit('refresh');
            } catch (error) {
                // 显示错误消息
                message.error('凭据更新失败')
            }
        }).catch((error) => {
            // 显示表单验证失败的消息
            message.error('请检查表单是否填写正确')
            console.log('验证失败:', error)
        })
    })
}

// 处理模态框的取消按钮点击事件
const handleCancel = () => {
    // 关闭模态框
    isVisible.value = false
    // 重置表单
    resetForm()
}

// 公开在此组件之外使用的功能
defineExpose({
    showEditModal: (credential) => {
        form.id = credential.id
        form.name = credential.name
        form.type = credential.type
        form.account = credential.account
        form.notes = credential.notes

        form.password = '' // 确保密码字段为空
        form.key = '' // 确保密钥字段为空
        form.key_password = '' // 确保密钥密码字段为空
        form.KeyId = credential.KeyId // 填充Key ID，如果存在
        form.KeySecret = '' // 确保KeySecret字段为空

        isVisible.value = true
    }
})
</script>