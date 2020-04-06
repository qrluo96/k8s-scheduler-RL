package client

import (
	"context"
	"encoding/json"
	"flag"
	"log"
	"time"

	pb "simulator/protos"

	"simulator/pkg/clock"
	"simulator/pkg/metrics"
	"simulator/pkg/util"

	v1 "k8s.io/api/core/v1"
)

var Client pb.SimRPCClient

var (
	tls                = flag.Bool("tls", false, "Connection uses TLS if true, else plain TCP")
	caFile             = flag.String("ca_file", "", "The file containing the CA root cert file")
	serverAddr         = flag.String("server_addr", "localhost:10000", "The server address in the format of host:port")
	serverHostOverride = flag.String("server_host_override", "x.test.youtube.com", "The server name use to verify the hostname returned by TLS handshake")
)

// SendFormattedMetrics a test function for sending metrics to server
func SendFormattedMetrics(met *metrics.Metrics) {
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

// SendPodMetrics a test function for sending metrics to server
// test
// func SendPodMetrics(met *metrics.Metrics) string {
// 	var formatter = metrics.JSONFormatter{}

// 	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
// 	defer cancel()

// 	var str, _ = formatter.Format(met)
// 	var metric = pb.PodMetrics{PodMetrics: str}

// 	r, err := Client.RecordPodMetrics(ctx, &metric)
// 	if err != nil {
// 		log.Fatalf("could not greet: %v", err)
// 	}
// 	log.Printf("Greeting: %d", r.GetResult())

// 	return r.Result
// }

// SendPodOnlyMetrics a test function for sending metrics to server
// test

type podMetric struct {
	Clock clock.Clock `json: "Clock"`
	Pod   *v1.Pod     `json:",inline"`
}

// ListScheduleResult get the remote schedule result
func ListScheduleResult(clock clock.Clock, pod *v1.Pod) util.ScheduleResult {
	podMetric := podMetric{
		Clock: clock,
		Pod:   pod,
	}

	bytes, _ := json.Marshal(podMetric)
	podData := string(bytes)

	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Second)
	defer cancel()

	var metric = pb.PodMetrics{PodMetrics: podData}

	r, err := Client.ListScheduleResult(ctx, &metric)
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}
	log.Printf("Greeting: %d", r.GetScheduleProcess())

	result := util.ScheduleResult{}
	result.SuggestHost = r.GetSuggestHost()
	result.EvaluatedNodes = int(r.GetEvaluatedNodes())
	result.FeasibleNodes = int(r.GetFeasibleNodes())
	result.ScheduleProcess = int(r.GetScheduleProcess())

	return result
}

// SendPodOnlyMetrics a test function for sending metrics to server
// test
func SendPodOnlyMetrics(clock clock.Clock, pod *v1.Pod) string {
	podMetric := podMetric{
		Clock: clock,
		Pod:   pod,
	}

	bytes, _ := json.Marshal(podMetric)
	podData := string(bytes)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// var str, _ = formatter.Format(met)
	var metric = pb.PodMetrics{PodMetrics: podData}

	r, err := Client.RecordPodMetrics(ctx, &metric)
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}
	log.Printf("Greeting: %d", r.GetResult())

	return r.Result
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
