package scheduler

import (
	v1 "k8s.io/api/core/v1"

	"simulator/pkg/clock"
	"simulator/pkg/util"
)

func updatePodStatusSchedulingSucceess(clock clock.Clock, pod *v1.Pod) {
	util.UpdatePodCondition(clock, &pod.Status, &v1.PodCondition{
		Type:          v1.PodScheduled,
		Status:        v1.ConditionTrue,
		LastProbeTime: clock.ToMetaV1(),
		// Reason:
		// Message:
	})
}

func updatePodStatusSchedulingFailure(clock clock.Clock, pod *v1.Pod, err error) {
	util.UpdatePodCondition(clock, &pod.Status, &v1.PodCondition{
		Type:          v1.PodScheduled,
		Status:        v1.ConditionFalse,
		LastProbeTime: clock.ToMetaV1(),
		Reason:        v1.PodReasonUnschedulable,
		Message:       err.Error(),
	})
}
