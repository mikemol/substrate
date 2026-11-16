#!/usr/bin/env bash
# Forced-interleaving witness for the post-commit marker check (substrate:W382).
#
# 1. OLD SHAPE FAILS DETERMINISTICALLY: a producer writes the marker FIRST and then
#    far more than a pipe buffer; `grep -q` exits at the marker; the producer's next
#    write gets EPIPE and dies of SIGPIPE (141); under pipefail the pipeline fails
#    although the marker is present. No timing luck: what follows the marker exceeds
#    the pipe buffer, so the producer cannot finish first.
# 2. NEW SHAPE CANNOT FAIL THAT WAY: in a throwaway repo, a commit with a large body
#    and a `Post-Commit-Advisory: done` trailer is read with
#    `git log -1 --format='%(trailers:key=Post-Commit-Advisory,valueonly)'`, which
#    emits only the trailer value; there is no early-exit consumer.
# 3. And a large body WITHOUT the trailer reads empty (no false positive from text
#    in the body that looks like the marker).
#
# Exit 0 only if all three hold. Writes only inside a mktemp directory it removes.
set -uo pipefail

fail=0
marker='Post-Commit-Advisory: done'

producer() {
  printf '%s\n' "$marker"
  head -c 8388608 /dev/zero | tr '\0' 'x'
  printf '\n'
}

if producer | grep -q "$marker"; then
  echo "FAIL 1: grep -q under pipefail passed; the witness did not force SIGPIPE"
  fail=1
else
  st=("${PIPESTATUS[@]}")
  if [ "${st[0]}" = 141 ] && [ "${st[1]}" = 0 ]; then
    echo "ok 1: old shape fails with marker present (producer=141 grep=0)"
  else
    echo "FAIL 1: unexpected statuses producer=${st[0]} grep=${st[1]}"
    fail=1
  fi
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
git -C "$tmp" init -q
git -C "$tmp" config user.email witness@example.invalid
git -C "$tmp" config user.name witness

# Messages go through files (-F): a >2 MiB message exceeds the argument-length limit.
write_msg() {  # $1 = file, $2 = with|without trailer
  {
    printf 'subject\n\n'
    head -c 2097152 /dev/zero | tr '\0' 'y'
    printf '\npost-commit advisory (auto-captured):\n'
    printf '    text that looks like a marker: Post-Commit-Advisory: done\n'
    if [ "$2" = with ]; then
      printf '\nPost-Commit-Advisory: done\n'
    else
      printf '    and more body text\n'
    fi
  } >"$1"
}

trailer() {
  git -C "$tmp" log -1 --format='%(trailers:key=Post-Commit-Advisory,valueonly)'
}

write_msg "$tmp/msg_with" with
if ! git -C "$tmp" commit -q --allow-empty --no-verify -F "$tmp/msg_with"; then
  echo "FAIL 2: could not create the witness commit"
  exit 1
fi
got="$(trailer)"
if [ "$got" = "done" ]; then
  echo "ok 2: trailer read finds the marker on a >2 MiB message"
else
  echo "FAIL 2: trailer read returned '${got}'"
  fail=1
fi

write_msg "$tmp/msg_without" without
if ! git -C "$tmp" commit -q --allow-empty --no-verify -F "$tmp/msg_without"; then
  echo "FAIL 3: could not create the witness commit"
  exit 1
fi
got="$(trailer)"
if [ -z "$got" ]; then
  echo "ok 3: no trailer means empty, despite marker-like body text"
else
  echo "FAIL 3: trailer read returned '${got}' with no trailer present"
  fail=1
fi

exit "$fail"
