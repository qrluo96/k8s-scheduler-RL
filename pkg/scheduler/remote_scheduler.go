// Copyright 2019 Preferred Networks, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Modifications copyright 2020 Qirui Luo.

package scheduler

import (
	"errors"
	"fmt"

	"github.com/containerd/containerd/log"
	v1 "k8s.io/api/core/v1"
	"k8s.io/kubernetes/pkg/scheduler/algorithm"
	"k8s.io/kubernetes/pkg/scheduler/algorithm/predicates"
	"k8s.io/kubernetes/pkg/scheduler/algorithm/priorities"
	"k8s.io/kubernetes/pkg/scheduler/api"
	"k8s.io/kubernetes/pkg/scheduler/core"
	"k8s.io/kubernetes/pkg/scheduler/nodeinfo"

	"simulator/pkg/client"
	"simulator/pkg/clock"
	l "simulator/pkg/log"
	"simulator/pkg/queue"
	"simulator/pkg/util"
)

// RemoteScheduler makes scheduling decision for each given pod in the one-by-one manner.
// This type is similar to "k8s.io/pkg/Scheduler/Scheduler/core".genericScheduler, which implements
// "k8s.io/pkg/Scheduler/Scheduler/core".ScheduleAlgorithm.
type RemoteScheduler struct {
	extenders    []Extender
	predicates   map[string]predicates.FitPredicate
	prioritizers []priorities.PriorityConfig

	lastNodeIndex     uint64
	preemptionEnabled bool
}

// NewRemoteScheduler creates a new RemoteScheduler.
func NewRemoteScheduler(preeptionEnabled bool) RemoteScheduler {
	return RemoteScheduler{
		predicates:        map[string]predicates.FitPredicate{},
		preemptionEnabled: preeptionEnabled,
	}
}

// AddExtender adds an extender to this GenericScheduler.
func (sched *RemoteScheduler) AddExtender(extender Extender) {
	sched.extenders = append(sched.extenders, extender)
}

// AddPredicate adds a predicate plugin to this GenericScheduler.
func (sched *RemoteScheduler) AddPredicate(name string, predicate predicates.FitPredicate) {
	sched.predicates[name] = predicate
}

// AddPrioritizer adds a prioritizer plugin to this GenericScheduler.
func (sched *RemoteScheduler) AddPrioritizer(prioritizer priorities.PriorityConfig) {
	sched.prioritizers = append(sched.prioritizers, prioritizer)
}

// Schedule implements remote Scheduler interface.
// Schedules pods in one-by-one manner by using registered extenders and plugins.
// schedule入口
// events, err := k.scheduler.Schedule(k.clock, k.pendingPods, k, nodeInfoMap)
func (sched *RemoteScheduler) Schedule(
	clock clock.Clock,
	pendingPods queue.PodQueue,
	// nodeLister is obj KubeSim
	nodeLister algorithm.NodeLister,
	nodeInfoMap map[string]*nodeinfo.NodeInfo) ([]Event, error) {

	results := []Event{}

	for {
		// For each pod popped from the front of the queue, ...
		pod, err := pendingPods.Front() // not pop a pod here; it may fail to any node
		if err != nil {
			if err == queue.ErrEmptyQueue {
				break
			} else {
				return []Event{}, errors.New("Unexpected error raised by Queueu.Pop()")
			}
		}

		log.L.Tracef("Trying to schedule pod %v", pod)

		podKey, err := util.PodKey(pod)
		if err != nil {
			return []Event{}, err
		}
		log.L.Debugf("Trying to schedule pod %s", podKey)

		// Send pod info to server
		_ = sched.sendPodInfo(clock, pod)

		// ... try to bind the pod to a node.
		result, err := sched.ScheduleOne(clock, pod, nodeLister, nodeInfoMap, pendingPods)

		if err != nil {
			log.L.Tracef("Pod %v does not fit in any node", pod)
			log.L.Debugf("Pod %s does not fit in any node", podKey)

			return []Event{}, nil
		}

		// If found a node that can accommodate the pod, ...
		log.L.Debugf("Selected node %s", result.SuggestedHost)

		pod, _ = pendingPods.Pop()
		updatePodStatusSchedulingSucceess(clock, pod)
		if err := pendingPods.RemoveNominatedNode(pod); err != nil {
			return []Event{}, err
		}

		nodeInfo, ok := nodeInfoMap[result.SuggestedHost]
		if !ok {
			return []Event{}, fmt.Errorf("No node named %s", result.SuggestedHost)
		}
		nodeInfo.AddPod(pod)

		// ... then bind it to the node.
		results = append(results, &BindEvent{Pod: pod, ScheduleResult: result})
	}

	return results, nil
}

var _ = Scheduler(&RemoteScheduler{})

// func (sched *RemoteScheduler) remoteTest(
// 	clock clock.Clock,
// 	// the pod to be scheduled
// 	pod *v1.Pod,
// ) string {
// 	met, err := metrics.BuildPodMetrics(clock, pod)
// 	if err != nil {
// 		log.L.Debug(err)
// 	}
// 	r := client.SendPodMetrics(&met)

// 	log.L.Info(r)

// 	return r
// }

// type podMetric struct {
// 	Clock clock.Clock `json: "Clock"`
// 	Pod   *v1.Pod     `json:",inline"`
// }

func (sched *RemoteScheduler) sendPodInfo(
	clock clock.Clock,
	// the pod to be scheduled
	pod *v1.Pod,
) string {
	r := client.SendPodOnlyMetrics(clock, pod)

	log.L.Info(r)

	return r
}

func (sched *RemoteScheduler) ScheduleOne(
	clock clock.Clock,
	// the pod to be scheduled
	pod *v1.Pod,
	// obj KubeSim
	nodeLister algorithm.NodeLister,
	nodeInfoMap map[string]*nodeinfo.NodeInfo,
	podQueue queue.PodQueue) (core.ScheduleResult, error) {

	result := core.ScheduleResult{}
	// Send information of the pod that to be scheduled
	remoteResult := client.ListScheduleResult(clock, pod)

	ScheduleProcess := remoteResult.ScheduleProcess
	if ScheduleProcess != 0 {
		err := errors.New("Not fit into any node")

		return result, err
	}

	// TODO: complete the result part
	result.EvaluatedNodes = remoteResult.EvaluatedNodes
	result.FeasibleNodes = remoteResult.FeasibleNodes
	result.SuggestedHost = remoteResult.SuggestHost

	return result, nil
}

//
func (sched *RemoteScheduler) filter(
	pod *v1.Pod,
	nodes []*v1.Node,
	nodeInfoMap map[string]*nodeinfo.NodeInfo,
	podQueue queue.PodQueue,
) ([]*v1.Node, core.FailedPredicateMap, error) {

	if l.IsDebugEnabled() {
		nodeNames := make([]string, 0, len(nodes))
		for _, node := range nodes {
			nodeNames = append(nodeNames, node.Name)
		}
		log.L.Debugf("Filtering nodes %v", nodeNames)
	}

	// In-process plugins
	filtered, failedPredicateMap, err := filterWithPlugins(pod, sched.predicates, nodes, nodeInfoMap, podQueue)
	if err != nil {
		return []*v1.Node{}, core.FailedPredicateMap{}, err
	}

	if l.IsDebugEnabled() {
		nodeNames := make([]string, 0, len(filtered))
		for _, node := range filtered {
			nodeNames = append(nodeNames, node.Name)
		}
		log.L.Debugf("Plugins filtered nodes %v", nodeNames)
	}

	// Extenders
	if len(filtered) > 0 && len(sched.extenders) > 0 {
		for _, extender := range sched.extenders {
			var err error
			filtered, err = extender.filter(pod, filtered, nodeInfoMap, failedPredicateMap)
			if err != nil {
				return []*v1.Node{}, core.FailedPredicateMap{}, err
			}

			if len(filtered) == 0 {
				break
			}
		}
	}

	if l.IsDebugEnabled() {
		nodeNames := make([]string, 0, len(filtered))
		for _, node := range filtered {
			nodeNames = append(nodeNames, node.Name)
		}
		log.L.Debugf("Filtered nodes %v", nodeNames)
	}

	return filtered, failedPredicateMap, nil
}

func (sched *RemoteScheduler) prioritize(
	pod *v1.Pod,
	filteredNodes []*v1.Node,
	nodeInfoMap map[string]*nodeinfo.NodeInfo,
	podQueue queue.PodQueue) (api.HostPriorityList, error) {

	if l.IsDebugEnabled() {
		nodeNames := make([]string, 0, len(filteredNodes))
		for _, node := range filteredNodes {
			nodeNames = append(nodeNames, node.Name)
		}
		log.L.Debugf("Prioritizing nodes %v", nodeNames)
	}

	// If no priority configs are provided, then the EqualPriority function is applied.
	// This is required to generate the priority list in the required format.
	if len(sched.prioritizers) == 0 && len(sched.extenders) == 0 {
		prioList := make(api.HostPriorityList, 0, len(filteredNodes))

		for _, node := range filteredNodes {
			nodeInfo, ok := nodeInfoMap[node.Name]
			if !ok {
				return api.HostPriorityList{}, fmt.Errorf("No node named %s", node.Name)
			}

			prio, err := core.EqualPriorityMap(pod, &dummyPriorityMetadata{}, nodeInfo)
			if err != nil {
				return api.HostPriorityList{}, err
			}
			prioList = append(prioList, prio)
		}

		return prioList, nil
	}

	// In-process plugins
	prioList, err := prioritizeWithPlugins(pod, sched.prioritizers, filteredNodes, nodeInfoMap, podQueue)
	if err != nil {
		return api.HostPriorityList{}, err
	}

	if l.IsDebugEnabled() {
		nodeNames := make([]string, 0, len(filteredNodes))
		for _, node := range filteredNodes {
			nodeNames = append(nodeNames, node.Name)
		}
		log.L.Debugf("Plugins prioritized nodes %v", nodeNames)
	}

	// Extenders
	if len(sched.extenders) > 0 {
		prioMap := map[string]int{}
		for _, extender := range sched.extenders {
			extender.prioritize(pod, filteredNodes, prioMap)
		}

		for i, prio := range prioList {
			prioList[i].Score += prioMap[prio.Host]
		}
	}

	log.L.Debugf("Prioritized nodes %v", prioList)

	return prioList, nil
}

func (sched *RemoteScheduler) preempt(
	preemptor *v1.Pod,
	podQueue queue.PodQueue,
	nodeLister algorithm.NodeLister,
	nodeInfoMap map[string]*nodeinfo.NodeInfo,
	fitError *core.FitError) ([]Event, error) {

	node, victims, nominatedPodsToClear, err := sched.findPreemption(
		preemptor, podQueue, nodeLister, nodeInfoMap, fitError)
	if err != nil {
		return []Event{}, err
	}

	delEvents := make([]Event, 0, len(victims))
	if node != nil {
		log.L.Tracef("Node %v selected for victim", node)
		log.L.Debugf("Node %s selected for victim", node.Name)

		// Nominate the victim node for the preemptor pod.
		if err := podQueue.UpdateNominatedNode(preemptor, node.Name); err != nil {
			return []Event{}, err
		}

		// Delete the victim pods.
		for _, victim := range victims {
			log.L.Tracef("Pod %v selected for victim", victim)

			if l.IsDebugEnabled() {
				key, err := util.PodKey(victim)
				if err != nil {
					return []Event{}, err
				}
				log.L.Debugf("Pod %s selected for victim", key)
			}

			event := DeleteEvent{PodNamespace: victim.Namespace, PodName: victim.Name, NodeName: node.Name}
			delEvents = append(delEvents, &event)
		}
	}

	// Clear nomination of pods that previously have nomination.
	for _, pod := range nominatedPodsToClear {
		log.L.Tracef("Nomination of pod %v cleared", pod)

		if l.IsDebugEnabled() {
			key, err := util.PodKey(pod)
			if err != nil {
				return []Event{}, err
			}
			log.L.Debugf("Nomination of pod %s cleared", key)
		}

		if err := podQueue.RemoveNominatedNode(pod); err != nil {
			return []Event{}, err
		}
	}

	return delEvents, nil
}

func (sched *RemoteScheduler) findPreemption(
	preemptor *v1.Pod,
	podQueue queue.PodQueue,
	nodeLister algorithm.NodeLister,
	nodeInfoMap map[string]*nodeinfo.NodeInfo,
	fitError *core.FitError,
) (selectedNode *v1.Node, preemptedPods []*v1.Pod, cleanupNominatedPods []*v1.Pod, err error) {

	preemptorKey, err := util.PodKey(preemptor)
	if err != nil {
		return nil, nil, nil, err
	}

	if !podEligibleToPreemptOthers(preemptor, nodeInfoMap) {
		log.L.Debugf("Pod %s is not eligible for more preemption", preemptorKey)
		return nil, nil, nil, nil
	}

	allNodes, err := nodeLister.List()
	if err != nil {
		return nil, nil, nil, err
	}

	if len(allNodes) == 0 {
		return nil, nil, nil, core.ErrNoNodesAvailable
	}

	potentialNodes := nodesWherePreemptionMightHelp(allNodes, fitError.FailedPredicates)
	if len(potentialNodes) == 0 {
		log.L.Debugf("Preemption will not help schedule pod %s on any node.", preemptorKey)
		// In this case, we should clean-up any existing nominated node name of the pod.
		return nil, nil, []*v1.Pod{preemptor}, nil
	}

	// pdbs, err := sched.pdbLister.List(labels.Everything())
	// if err != nil {
	// 	return nil, nil, nil, err
	// }

	nodeToVictims, err := sched.selectNodesForPreemption(preemptor, nodeInfoMap, potentialNodes, podQueue /* , pdb */)
	if err != nil {
		return nil, nil, nil, err
	}

	// // We will only check nodeToVictims with extenders that support preemption.
	// // Extenders which do not support preemption may later prevent preemptor from being scheduled on the nominated
	// // node. In that case, scheduler will find a different host for the preemptor in subsequent scheduling cycles.
	// nodeToVictims, err = g.processPreemptionWithExtenders(pod, nodeToVictims)
	// if err != nil {
	// 	return nil, nil, nil, err
	// }

	candidateNode := pickOneNodeForPreemption(nodeToVictims)
	if candidateNode == nil {
		return nil, nil, nil, nil
	}

	// Lower priority pods nominated to run on this node, may no longer fit on this node.
	// So, we should remove their nomination.
	// Removing their nomination updates these pods and moves them to the active queue.
	// It lets scheduler find another place for them.
	nominatedPods := getLowerPriorityNominatedPods(preemptor, candidateNode.Name, podQueue)
	if nodeInfo, ok := nodeInfoMap[candidateNode.Name]; ok {
		return nodeInfo.Node(), nodeToVictims[candidateNode].Pods, nominatedPods, nil
	}

	return nil, nil, nil, fmt.Errorf("No node named %s in nodeInfoMap", candidateNode.Name)
}
