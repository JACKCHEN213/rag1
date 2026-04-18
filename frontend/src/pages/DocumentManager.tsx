import React, { useState } from 'react';
import { Button, Upload, message, Table } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const DocumentManager: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);

  const uploadProps = {
    name: 'file',
    action: '/api/documents/upload',
    onChange(info: any) {
      if (info.file.status === 'done') {
        message.success(`${info.file.name} uploaded successfully`);
      } else if (info.file.status === 'error') {
        message.error(`${info.file.name} upload failed.`);
      }
    },
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Filename',
      dataIndex: 'filename',
      key: 'filename',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
    },
  ];

  return (
    <div className="section">
      <h2>Document Manager</h2>
      <Upload {...uploadProps}>
        <Button icon={<UploadOutlined />}>Upload Document</Button>
      </Upload>
      
      <div style={{ marginTop: 20 }}>
        <Table 
          columns={columns} 
          dataSource={documents} 
          rowKey="id"
          locale={{ emptyText: 'No documents uploaded yet' }}
        />
      </div>
    </div>
  );
};

export default DocumentManager;
