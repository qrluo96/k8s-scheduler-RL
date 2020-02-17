package client

import (
	"context"
	"flag"
	"log"
	"time"

	pb "simulator/protos"

	"simulator/pkg/metrics"
)

var Client pb.SimRPCClient

var (
	tls                = flag.Bool("tls", false, "Connection uses TLS if true, else plain TCP")
	caFile             = flag.String("ca_file", "", "The file containing the CA root cert file")
	serverAddr         = flag.String("server_addr", "localhost:10000", "The server address in the format of host:port")
	serverHostOverride = flag.String("server_host_override", "x.test.youtube.com", "The server name use to verify the hostname returned by TLS handshake")
)

// SendFormattedMetrics a test function for sending metrics to server
func SendFormattedMetrics(met *metrics.Metrics, metricsWriters []metrics.Writer) {
	var formatter = metrics.JSONFormatter{}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var str, _ = formatter.Format(met)
	var metric = pb.FormattedMetrics{FormattedMetrics: str}

	r, err := Client.RecordFormattedMetrics(ctx, &metric)
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}
	log.Printf("Greeting: %d", r.GetResult())
}

// SendMetric comment.
func SendMetric(metric *pb.Metrics) {
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	r, err := Client.RecordMetrics(ctx, metric)
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}
	log.Printf("Greeting: %d", r.GetResult())
}

// InitMetric comment.
func InitMetric(metric *pb.Metrics, clockStr string, nodeStr string) {
	var clock pb.Clock = pb.Clock{ClockMetrics_Key: clockStr}
	var node pb.Nodes = pb.Nodes{NodesMetricsKey: nodeStr}
	var pod pb.Pods = pb.Pods{PodsMetricsKey: "test pod"}
	var queue pb.Queue = pb.Queue{QueueMetricsKey: "test queue"}
	metric.Clock = &clock
	metric.Nodes = &node
	metric.Pods = &pod
	metric.Queue = &queue
}
