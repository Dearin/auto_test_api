#!/bin/bash
# Script to generate zone file.
# Author: tianzhankui
# History:
#  2020/12/21 v0.8 First Release.


read -d '' usage << EOF
# Usage:
## 1. run this script whitout args will gengerate a default zone file.
## example:  ./gen_zone.sh
## 2. run this script wiht one args to specify zone name,   two args to specify zone name and TTL.
## example: ./gen_zone.sh com1 
## example: ./gen_zone.sh com1 3200
EOF


if [ "$1" == '-h' ];then
	echo "${usage}"
	exit
fi


zone_name=${1:-aaaaa.bbbbb.ccccc.ddddd.eeeee}
TTL=${2:-3600}

read -d '' zone_file_head << EOF
${zone_name}. ${TTL} SOA ns.${zone_name}. root.${zone_name}. 1 3600 3600 3600 3600
${zone_name}. ${TTL} NS ns.${zone_name}.
ns.${zone_name}. ${TTL} A 127.0.0.1
EOF

gen_rr()
{
    for((i=1;i<=615;i+=8))
    do
        rr_prefix1=abcdefg$[$i+1]
        rr_prefix2=abcdefg$[$i+2]
        rr_prefix3=abcdefg$[$i+3]
        rr_prefix4=abcdefg$[$i+4]
        rr_prefix5=abcdefg$[$i+5]
        rr_prefix6=abcdefg$[$i+8]
read -d  ''  base_resource_record  << EOF
${rr_prefix1}.${zone_name}. ${TTL} IN A 10.10.11.1
${rr_prefix1}.${zone_name}. ${TTL} IN MX 10 ${rr_prefix1}.${zone_name}.
${rr_prefix1}.${zone_name}. ${TTL} IN AAAA AB01::BC02
${rr_prefix1}.${zone_name}. ${TTL} IN TXT "v=spf1 +a +mx -all"
${rr_prefix1}.${zone_name}. ${TTL} IN SPF "v=spf1 +a +mx -all"
${rr_prefix2}.${zone_name}. ${TTL} IN CNAME ${rr_prefix1}.${zone_name}.
${rr_prefix3}.${zone_name}. ${TTL} IN SRV 1 0 9876 ${rr_prefix1}.${zone_name}.
${rr_prefix4}.${zone_name}. ${TTL} IN NAPTR 101 10 "u" "sip+E2U" "!^.*$!sip:userA@zdns.cn!" .
${rr_prefix4}.${zone_name}. ${TTL} IN A 1.1.1.4
${rr_prefix5}.${zone_name}. ${TTL} IN A 1.1.1.5
${rr_prefix1}.${zone_name}. ${TTL} IN DNAME ${rr_prefix4}.${zone_name}.
${rr_prefix1}.${zone_name}. ${TTL} IN CAA 0 issue "letsencrypt.org"
${rr_prefix6}.${zone_name}. ${TTL} IN PTR  ${rr_prefix1}.${zone_name}.
EOF
        echo "${base_resource_record}"
    done
}

zone_file_body=$(gen_rr)

echo "${zone_file_head}" > ${zone_name}.txt
echo "${zone_file_body}" >> ${zone_name}.txt

echo "Generate finished: $(pwd)/${zone_name}.txt"
