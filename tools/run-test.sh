#!/bin/sh
# usage: tools/run-test.sh [19.0]
# Starts a throwaway Postgres and Odoo in Docker and checks the module twice:
#   1. imported as a zip through Apps > Import Module, as on Odoo Online;
#   2. installed from the addons path, as on Odoo.sh and on-premise.
set -e
V=${1:-19.0}; HERE=$(cd "$(dirname "$0")/.." && pwd); T=$(mktemp -d); N=amcp-odoo-test
cleanup() { docker rm -f $N-db $N >/dev/null 2>&1 || true; docker network rm $N-net >/dev/null 2>&1 || true; rm -rf "$T"; }
trap cleanup EXIT
mkdir -p "$T/addons" "$T/empty"; cp -R "$HERE/anythingmcp_connector" "$T/addons/"
(cd "$T/addons" && zip -qr "$T/anythingmcp_connector.zip" anythingmcp_connector -x '*/.*')
docker rm -f $N-db $N >/dev/null 2>&1 || true
docker network create $N-net >/dev/null
docker run -d --name $N-db --network $N-net -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres postgres:16 >/dev/null
sleep 6
# The image entrypoint reads the database connection from HOST, USER, PASSWORD.
DB="-e HOST=$N-db -e USER=odoo -e PASSWORD=odoo"
serve() { # $1 = addons dir, $2 = database
  docker run -d --name $N --network $N-net $DB -p 18069:8069 -v "$1":/mnt/extra-addons:ro odoo:$V odoo -d "$2" --db-filter="^$2\$" >/dev/null
  for i in $(seq 60); do curl -sf -o /dev/null http://localhost:18069/web/login && return 0; sleep 2; done
  docker logs --tail 40 $N; exit 1
}
echo "== imported as a zip (Odoo Online)"
docker run --rm --network $N-net $DB -v "$T/empty":/mnt/extra-addons:ro odoo:$V odoo -d imported -i base_setup,base_import_module --load-language=it_IT --stop-after-init --log-level=warn
serve "$T/empty" imported
python3 "$HERE/tools/check_module.py" http://localhost:18069 imported "$T/anythingmcp_connector.zip" || { docker logs --tail 40 $N; exit 1; }
docker rm -f $N >/dev/null
echo "== installed from the addons path (Odoo.sh, on-premise)"
docker run --rm --network $N-net $DB -v "$T/addons":/mnt/extra-addons:ro odoo:$V odoo -d classic -i anythingmcp_connector --load-language=it_IT --stop-after-init --log-level=warn
serve "$T/addons" classic
python3 "$HERE/tools/check_module.py" http://localhost:18069 classic || { docker logs --tail 40 $N; exit 1; }
