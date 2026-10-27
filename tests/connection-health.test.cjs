const assert=require('node:assert/strict');
const {classifyConnection}=require('../guardian/connection-health.cjs');
assert.equal(classifyConnection({clientRunning:true,transportReady:false}).health,'attention');
assert.equal(classifyConnection({clientRunning:true,transportReady:false}).uiMounted,false);
assert.equal(classifyConnection({clientRunning:false,transportReady:false}).health,'idle');
assert.equal(classifyConnection({clientRunning:true,transportReady:true}).health,'transport_ready');
assert.equal(classifyConnection({clientRunning:true,transportReady:true}).uiMounted,null);
console.log('5项检查通过：未连接不报正常、客户端退出不报故障、端口可用不冒充UI已显示。');
