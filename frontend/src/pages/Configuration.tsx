import React, { useState } from 'react';
import { Form, Input, Button, Select, message } from 'antd';

const Configuration: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = (values: any) => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      message.success('Configuration saved successfully!');
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="section">
      <h2>Configuration</h2>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{
          llm_provider: 'openai',
          embedding_model: 'BAAI/bge-m3',
          chunk_size: 512,
        }}
      >
        <Form.Item
          name="llm_provider"
          label="LLM Provider"
          rules={[{ required: true, message: 'Please select LLM provider' }]}
        >
          <Select>
            <Select.Option value="openai">OpenAI</Select.Option>
            <Select.Option value="claude">Claude</Select.Option>
            <Select.Option value="local">Local Model</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="api_key"
          label="API Key"
        >
          <Input.Password placeholder="Enter your API key" />
        </Form.Item>

        <Form.Item
          name="embedding_model"
          label="Embedding Model"
        >
          <Select>
            <Select.Option value="BAAI/bge-m3">BGE-M3</Select.Option>
            <Select.Option value="text-embedding-ada-002">Ada-002</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="chunk_size"
          label="Chunk Size"
          rules={[{ required: true, message: 'Please enter chunk size' }]}
        >
          <Input type="number" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Save Configuration
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default Configuration;
