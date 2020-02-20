// Code generated by protoc-gen-go. DO NOT EDIT.
// source: k8s_sim.proto

package simRPC

import (
	context "context"
	fmt "fmt"
	proto "github.com/golang/protobuf/proto"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
	math "math"
)

// Reference imports to suppress errors if they are not otherwise used.
var _ = proto.Marshal
var _ = fmt.Errorf
var _ = math.Inf

// This is a compile-time assertion to ensure that this generated file
// is compatible with the proto package it is being compiled against.
// A compilation error at this line likely means your copy of the
// proto package needs to be updated.
const _ = proto.ProtoPackageIsVersion3 // please upgrade the proto package

// 测试
// 返回四个关键值的str
type FormattedMetrics struct {
	FormattedMetrics     string   `protobuf:"bytes,1,opt,name=formatted_metrics,json=formattedMetrics,proto3" json:"formatted_metrics,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *FormattedMetrics) Reset()         { *m = FormattedMetrics{} }
func (m *FormattedMetrics) String() string { return proto.CompactTextString(m) }
func (*FormattedMetrics) ProtoMessage()    {}
func (*FormattedMetrics) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{0}
}

func (m *FormattedMetrics) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_FormattedMetrics.Unmarshal(m, b)
}
func (m *FormattedMetrics) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_FormattedMetrics.Marshal(b, m, deterministic)
}
func (m *FormattedMetrics) XXX_Merge(src proto.Message) {
	xxx_messageInfo_FormattedMetrics.Merge(m, src)
}
func (m *FormattedMetrics) XXX_Size() int {
	return xxx_messageInfo_FormattedMetrics.Size(m)
}
func (m *FormattedMetrics) XXX_DiscardUnknown() {
	xxx_messageInfo_FormattedMetrics.DiscardUnknown(m)
}

var xxx_messageInfo_FormattedMetrics proto.InternalMessageInfo

func (m *FormattedMetrics) GetFormattedMetrics() string {
	if m != nil {
		return m.FormattedMetrics
	}
	return ""
}

type PodMetrics struct {
	PodMetrics           string   `protobuf:"bytes,1,opt,name=pod_metrics,json=podMetrics,proto3" json:"pod_metrics,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *PodMetrics) Reset()         { *m = PodMetrics{} }
func (m *PodMetrics) String() string { return proto.CompactTextString(m) }
func (*PodMetrics) ProtoMessage()    {}
func (*PodMetrics) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{1}
}

func (m *PodMetrics) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_PodMetrics.Unmarshal(m, b)
}
func (m *PodMetrics) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_PodMetrics.Marshal(b, m, deterministic)
}
func (m *PodMetrics) XXX_Merge(src proto.Message) {
	xxx_messageInfo_PodMetrics.Merge(m, src)
}
func (m *PodMetrics) XXX_Size() int {
	return xxx_messageInfo_PodMetrics.Size(m)
}
func (m *PodMetrics) XXX_DiscardUnknown() {
	xxx_messageInfo_PodMetrics.DiscardUnknown(m)
}

var xxx_messageInfo_PodMetrics proto.InternalMessageInfo

func (m *PodMetrics) GetPodMetrics() string {
	if m != nil {
		return m.PodMetrics
	}
	return ""
}

type Metrics struct {
	Clock                *Clock   `protobuf:"bytes,1,opt,name=clock,proto3" json:"clock,omitempty"`
	Nodes                *Nodes   `protobuf:"bytes,2,opt,name=nodes,proto3" json:"nodes,omitempty"`
	Pods                 *Pods    `protobuf:"bytes,3,opt,name=pods,proto3" json:"pods,omitempty"`
	Queue                *Queue   `protobuf:"bytes,4,opt,name=queue,proto3" json:"queue,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *Metrics) Reset()         { *m = Metrics{} }
func (m *Metrics) String() string { return proto.CompactTextString(m) }
func (*Metrics) ProtoMessage()    {}
func (*Metrics) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{2}
}

func (m *Metrics) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_Metrics.Unmarshal(m, b)
}
func (m *Metrics) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_Metrics.Marshal(b, m, deterministic)
}
func (m *Metrics) XXX_Merge(src proto.Message) {
	xxx_messageInfo_Metrics.Merge(m, src)
}
func (m *Metrics) XXX_Size() int {
	return xxx_messageInfo_Metrics.Size(m)
}
func (m *Metrics) XXX_DiscardUnknown() {
	xxx_messageInfo_Metrics.DiscardUnknown(m)
}

var xxx_messageInfo_Metrics proto.InternalMessageInfo

func (m *Metrics) GetClock() *Clock {
	if m != nil {
		return m.Clock
	}
	return nil
}

func (m *Metrics) GetNodes() *Nodes {
	if m != nil {
		return m.Nodes
	}
	return nil
}

func (m *Metrics) GetPods() *Pods {
	if m != nil {
		return m.Pods
	}
	return nil
}

func (m *Metrics) GetQueue() *Queue {
	if m != nil {
		return m.Queue
	}
	return nil
}

type Clock struct {
	ClockMetrics_Key     string   `protobuf:"bytes,1,opt,name=clock_metrics_Key,json=clockMetricsKey,proto3" json:"clock_metrics_Key,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *Clock) Reset()         { *m = Clock{} }
func (m *Clock) String() string { return proto.CompactTextString(m) }
func (*Clock) ProtoMessage()    {}
func (*Clock) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{3}
}

func (m *Clock) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_Clock.Unmarshal(m, b)
}
func (m *Clock) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_Clock.Marshal(b, m, deterministic)
}
func (m *Clock) XXX_Merge(src proto.Message) {
	xxx_messageInfo_Clock.Merge(m, src)
}
func (m *Clock) XXX_Size() int {
	return xxx_messageInfo_Clock.Size(m)
}
func (m *Clock) XXX_DiscardUnknown() {
	xxx_messageInfo_Clock.DiscardUnknown(m)
}

var xxx_messageInfo_Clock proto.InternalMessageInfo

func (m *Clock) GetClockMetrics_Key() string {
	if m != nil {
		return m.ClockMetrics_Key
	}
	return ""
}

type Nodes struct {
	NodesMetricsKey      string   `protobuf:"bytes,1,opt,name=nodes_metrics_key,json=nodesMetricsKey,proto3" json:"nodes_metrics_key,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *Nodes) Reset()         { *m = Nodes{} }
func (m *Nodes) String() string { return proto.CompactTextString(m) }
func (*Nodes) ProtoMessage()    {}
func (*Nodes) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{4}
}

func (m *Nodes) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_Nodes.Unmarshal(m, b)
}
func (m *Nodes) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_Nodes.Marshal(b, m, deterministic)
}
func (m *Nodes) XXX_Merge(src proto.Message) {
	xxx_messageInfo_Nodes.Merge(m, src)
}
func (m *Nodes) XXX_Size() int {
	return xxx_messageInfo_Nodes.Size(m)
}
func (m *Nodes) XXX_DiscardUnknown() {
	xxx_messageInfo_Nodes.DiscardUnknown(m)
}

var xxx_messageInfo_Nodes proto.InternalMessageInfo

func (m *Nodes) GetNodesMetricsKey() string {
	if m != nil {
		return m.NodesMetricsKey
	}
	return ""
}

type Pods struct {
	PodsMetricsKey       string   `protobuf:"bytes,1,opt,name=pods_metrics_key,json=podsMetricsKey,proto3" json:"pods_metrics_key,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *Pods) Reset()         { *m = Pods{} }
func (m *Pods) String() string { return proto.CompactTextString(m) }
func (*Pods) ProtoMessage()    {}
func (*Pods) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{5}
}

func (m *Pods) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_Pods.Unmarshal(m, b)
}
func (m *Pods) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_Pods.Marshal(b, m, deterministic)
}
func (m *Pods) XXX_Merge(src proto.Message) {
	xxx_messageInfo_Pods.Merge(m, src)
}
func (m *Pods) XXX_Size() int {
	return xxx_messageInfo_Pods.Size(m)
}
func (m *Pods) XXX_DiscardUnknown() {
	xxx_messageInfo_Pods.DiscardUnknown(m)
}

var xxx_messageInfo_Pods proto.InternalMessageInfo

func (m *Pods) GetPodsMetricsKey() string {
	if m != nil {
		return m.PodsMetricsKey
	}
	return ""
}

type Queue struct {
	QueueMetricsKey      string   `protobuf:"bytes,1,opt,name=queue_metrics_key,json=queueMetricsKey,proto3" json:"queue_metrics_key,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *Queue) Reset()         { *m = Queue{} }
func (m *Queue) String() string { return proto.CompactTextString(m) }
func (*Queue) ProtoMessage()    {}
func (*Queue) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{6}
}

func (m *Queue) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_Queue.Unmarshal(m, b)
}
func (m *Queue) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_Queue.Marshal(b, m, deterministic)
}
func (m *Queue) XXX_Merge(src proto.Message) {
	xxx_messageInfo_Queue.Merge(m, src)
}
func (m *Queue) XXX_Size() int {
	return xxx_messageInfo_Queue.Size(m)
}
func (m *Queue) XXX_DiscardUnknown() {
	xxx_messageInfo_Queue.DiscardUnknown(m)
}

var xxx_messageInfo_Queue proto.InternalMessageInfo

func (m *Queue) GetQueueMetricsKey() string {
	if m != nil {
		return m.QueueMetricsKey
	}
	return ""
}

type Result struct {
	Result               string   `protobuf:"bytes,1,opt,name=result,proto3" json:"result,omitempty"`
	XXX_NoUnkeyedLiteral struct{} `json:"-"`
	XXX_unrecognized     []byte   `json:"-"`
	XXX_sizecache        int32    `json:"-"`
}

func (m *Result) Reset()         { *m = Result{} }
func (m *Result) String() string { return proto.CompactTextString(m) }
func (*Result) ProtoMessage()    {}
func (*Result) Descriptor() ([]byte, []int) {
	return fileDescriptor_4c18405e8fba6db3, []int{7}
}

func (m *Result) XXX_Unmarshal(b []byte) error {
	return xxx_messageInfo_Result.Unmarshal(m, b)
}
func (m *Result) XXX_Marshal(b []byte, deterministic bool) ([]byte, error) {
	return xxx_messageInfo_Result.Marshal(b, m, deterministic)
}
func (m *Result) XXX_Merge(src proto.Message) {
	xxx_messageInfo_Result.Merge(m, src)
}
func (m *Result) XXX_Size() int {
	return xxx_messageInfo_Result.Size(m)
}
func (m *Result) XXX_DiscardUnknown() {
	xxx_messageInfo_Result.DiscardUnknown(m)
}

var xxx_messageInfo_Result proto.InternalMessageInfo

func (m *Result) GetResult() string {
	if m != nil {
		return m.Result
	}
	return ""
}

func init() {
	proto.RegisterType((*FormattedMetrics)(nil), "simRPC.FormattedMetrics")
	proto.RegisterType((*PodMetrics)(nil), "simRPC.PodMetrics")
	proto.RegisterType((*Metrics)(nil), "simRPC.Metrics")
	proto.RegisterType((*Clock)(nil), "simRPC.Clock")
	proto.RegisterType((*Nodes)(nil), "simRPC.Nodes")
	proto.RegisterType((*Pods)(nil), "simRPC.Pods")
	proto.RegisterType((*Queue)(nil), "simRPC.Queue")
	proto.RegisterType((*Result)(nil), "simRPC.Result")
}

func init() { proto.RegisterFile("k8s_sim.proto", fileDescriptor_4c18405e8fba6db3) }

var fileDescriptor_4c18405e8fba6db3 = []byte{
	// 339 bytes of a gzipped FileDescriptorProto
	0x1f, 0x8b, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0xff, 0x94, 0x52, 0xcd, 0x4e, 0xb3, 0x40,
	0x14, 0xfd, 0xf8, 0x6c, 0x31, 0xde, 0xda, 0x96, 0xce, 0xa2, 0x21, 0x6e, 0x6c, 0x70, 0xd3, 0x68,
	0x6c, 0x0c, 0xdd, 0xb8, 0xd2, 0x45, 0x8d, 0x9b, 0x46, 0x83, 0xf3, 0x02, 0x44, 0x61, 0x9a, 0x10,
	0x8a, 0x83, 0x0c, 0x2c, 0xfa, 0x2a, 0x3e, 0x8e, 0x4f, 0x66, 0xe6, 0xce, 0x0c, 0x02, 0xb2, 0x71,
	0x07, 0xe7, 0xe7, 0x9e, 0x73, 0xe1, 0xc2, 0x38, 0xbd, 0x15, 0xa1, 0x48, 0xb2, 0x55, 0x5e, 0xf0,
	0x92, 0x13, 0x5b, 0x24, 0x19, 0x0d, 0x36, 0xde, 0x3d, 0x38, 0x8f, 0xbc, 0xc8, 0x5e, 0xcb, 0x92,
	0xc5, 0x4f, 0xac, 0x2c, 0x92, 0x48, 0x90, 0x2b, 0x98, 0xed, 0x0c, 0x16, 0x66, 0x0a, 0x74, 0xad,
	0x85, 0xb5, 0x3c, 0xa1, 0xce, 0xae, 0x23, 0xf6, 0xae, 0x01, 0x02, 0x5e, 0x5b, 0xcf, 0x61, 0x94,
	0xf3, 0xae, 0x09, 0xf2, 0x5a, 0xe0, 0x7d, 0x5a, 0x70, 0x6c, 0xc4, 0x17, 0x30, 0x8c, 0xf6, 0x3c,
	0x4a, 0x51, 0x36, 0xf2, 0xc7, 0x2b, 0xd5, 0x69, 0xb5, 0x91, 0x20, 0x55, 0x9c, 0x14, 0xbd, 0xf3,
	0x98, 0x09, 0xf7, 0x7f, 0x5b, 0xf4, 0x2c, 0x41, 0xaa, 0x38, 0xb2, 0x80, 0x41, 0xce, 0x63, 0xe1,
	0x1e, 0xa1, 0xe6, 0xd4, 0x68, 0x02, 0x1e, 0x0b, 0x8a, 0x8c, 0x1c, 0xf3, 0x51, 0xb1, 0x8a, 0xb9,
	0x83, 0xf6, 0x98, 0x17, 0x09, 0x52, 0xc5, 0x79, 0x6b, 0x18, 0x62, 0x36, 0xb9, 0x84, 0x19, 0xa6,
	0x9b, 0x45, 0xc2, 0x2d, 0x3b, 0xe8, 0x65, 0xa6, 0x48, 0xe8, 0x15, 0xb6, 0xec, 0x20, 0x4d, 0xd8,
	0x45, 0x9a, 0xb0, 0x4d, 0x6d, 0x4a, 0x7f, 0x4c, 0x48, 0x34, 0x4c, 0x37, 0x30, 0x90, 0xe5, 0xc8,
	0x12, 0x1c, 0x59, 0xaf, 0xc7, 0x32, 0x91, 0x78, 0x3b, 0x06, 0xbb, 0xca, 0x18, 0x6c, 0xdb, 0x17,
	0x83, 0x44, 0xc3, 0xb4, 0x00, 0x9b, 0x32, 0x51, 0xed, 0x4b, 0x32, 0x07, 0xbb, 0xc0, 0x27, 0x2d,
	0xd5, 0x6f, 0xfe, 0x97, 0x05, 0xfa, 0x14, 0x88, 0x0f, 0x63, 0xca, 0x22, 0x5e, 0xd4, 0x3f, 0x73,
	0x6a, 0x3e, 0x92, 0x06, 0xce, 0x26, 0x06, 0x50, 0x43, 0xbd, 0x7f, 0xe4, 0x01, 0xe6, 0xca, 0xf3,
	0xeb, 0x88, 0x5c, 0xa3, 0xed, 0x32, 0x3d, 0x53, 0xee, 0xc0, 0x51, 0x53, 0x1a, 0x97, 0xf4, 0x07,
	0xff, 0x9b, 0x8d, 0x37, 0xbd, 0xfe, 0x0e, 0x00, 0x00, 0xff, 0xff, 0x37, 0xc7, 0xc7, 0x3f, 0xe4,
	0x02, 0x00, 0x00,
}

// Reference imports to suppress errors if they are not otherwise used.
var _ context.Context
var _ grpc.ClientConnInterface

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
const _ = grpc.SupportPackageIsVersion6

// SimRPCClient is the client API for SimRPC service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://godoc.org/google.golang.org/grpc#ClientConn.NewStream.
type SimRPCClient interface {
	RecordMetrics(ctx context.Context, in *Metrics, opts ...grpc.CallOption) (*Result, error)
	// A client-to-server streaming RPC.
	RecordFormattedMetrics(ctx context.Context, in *FormattedMetrics, opts ...grpc.CallOption) (*Result, error)
	RecordPodMetrics(ctx context.Context, in *FormattedMetrics, opts ...grpc.CallOption) (*Result, error)
}

type simRPCClient struct {
	cc grpc.ClientConnInterface
}

func NewSimRPCClient(cc grpc.ClientConnInterface) SimRPCClient {
	return &simRPCClient{cc}
}

func (c *simRPCClient) RecordMetrics(ctx context.Context, in *Metrics, opts ...grpc.CallOption) (*Result, error) {
	out := new(Result)
	err := c.cc.Invoke(ctx, "/simRPC.simRPC/RecordMetrics", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *simRPCClient) RecordFormattedMetrics(ctx context.Context, in *FormattedMetrics, opts ...grpc.CallOption) (*Result, error) {
	out := new(Result)
	err := c.cc.Invoke(ctx, "/simRPC.simRPC/RecordFormattedMetrics", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *simRPCClient) RecordPodMetrics(ctx context.Context, in *FormattedMetrics, opts ...grpc.CallOption) (*Result, error) {
	out := new(Result)
	err := c.cc.Invoke(ctx, "/simRPC.simRPC/RecordPodMetrics", in, out, opts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// SimRPCServer is the server API for SimRPC service.
type SimRPCServer interface {
	RecordMetrics(context.Context, *Metrics) (*Result, error)
	// A client-to-server streaming RPC.
	RecordFormattedMetrics(context.Context, *FormattedMetrics) (*Result, error)
	RecordPodMetrics(context.Context, *FormattedMetrics) (*Result, error)
}

// UnimplementedSimRPCServer can be embedded to have forward compatible implementations.
type UnimplementedSimRPCServer struct {
}

func (*UnimplementedSimRPCServer) RecordMetrics(ctx context.Context, req *Metrics) (*Result, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RecordMetrics not implemented")
}
func (*UnimplementedSimRPCServer) RecordFormattedMetrics(ctx context.Context, req *FormattedMetrics) (*Result, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RecordFormattedMetrics not implemented")
}
func (*UnimplementedSimRPCServer) RecordPodMetrics(ctx context.Context, req *FormattedMetrics) (*Result, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RecordPodMetrics not implemented")
}

func RegisterSimRPCServer(s *grpc.Server, srv SimRPCServer) {
	s.RegisterService(&_SimRPC_serviceDesc, srv)
}

func _SimRPC_RecordMetrics_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(Metrics)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(SimRPCServer).RecordMetrics(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/simRPC.simRPC/RecordMetrics",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(SimRPCServer).RecordMetrics(ctx, req.(*Metrics))
	}
	return interceptor(ctx, in, info, handler)
}

func _SimRPC_RecordFormattedMetrics_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(FormattedMetrics)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(SimRPCServer).RecordFormattedMetrics(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/simRPC.simRPC/RecordFormattedMetrics",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(SimRPCServer).RecordFormattedMetrics(ctx, req.(*FormattedMetrics))
	}
	return interceptor(ctx, in, info, handler)
}

func _SimRPC_RecordPodMetrics_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(FormattedMetrics)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(SimRPCServer).RecordPodMetrics(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: "/simRPC.simRPC/RecordPodMetrics",
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(SimRPCServer).RecordPodMetrics(ctx, req.(*FormattedMetrics))
	}
	return interceptor(ctx, in, info, handler)
}

var _SimRPC_serviceDesc = grpc.ServiceDesc{
	ServiceName: "simRPC.simRPC",
	HandlerType: (*SimRPCServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "RecordMetrics",
			Handler:    _SimRPC_RecordMetrics_Handler,
		},
		{
			MethodName: "RecordFormattedMetrics",
			Handler:    _SimRPC_RecordFormattedMetrics_Handler,
		},
		{
			MethodName: "RecordPodMetrics",
			Handler:    _SimRPC_RecordPodMetrics_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "k8s_sim.proto",
}
