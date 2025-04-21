package com.siem.model;

public class NetworkEvent {
    private final String sourceIp;
    private final String eventType;
    private final int count;

    public NetworkEvent(String sourceIp, String eventType, int count) {
        this.sourceIp = sourceIp;
        this.eventType = eventType;
        this.count = count;
    }

    public String getSourceIp() { return sourceIp; }
    public String getEventType() { return eventType; }
    public int getCount() { return count; }
}
