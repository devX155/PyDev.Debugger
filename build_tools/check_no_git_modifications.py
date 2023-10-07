import sys

expected_differences = set(line.strip() for line in r'''
--- a/_pydevd_bundle/pydevd_cython.c
+++ b/_pydevd_bundle/pydevd_cython.c
-  "_pydevd_bundle\\\\pydevd_cython.pyx",
-  "_pydevd_bundle\\\\pydevd_cython.pxd",
+  "_pydevd_bundle/pydevd_cython.pyx",
+  "_pydevd_bundle/pydevd_cython.pxd",
--- a/_pydevd_frame_eval/pydevd_frame_evaluator.c
+++ b/_pydevd_frame_eval/pydevd_frame_evaluator.c
-  "_pydevd_frame_eval\\\\pydevd_frame_evaluator.pyx",
+  "_pydevd_frame_eval/pydevd_frame_evaluator.pyx",
-  "_pydevd_bundle\\\\pydevd_cython.pxd",
+  "_pydevd_bundle/pydevd_cython.pxd",
'''.splitlines() if line.strip())


def main():
    import subprocess
    process = subprocess.Popen(
        'git status --porcelain'.split(), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, _ = process.communicate()
    if output:
        if sys.version_info[0] > 2:
            output = output.decode('utf-8')

        files = set()
        for line in output.splitlines():
            filename = line[3:]
            files.add(filename.strip())

        files.discard('.travis_install_python_deps.sh')
        files.discard('miniconda.sh')
        files.discard('build_tools/check_no_git_modifications.py')
        pydevd_cython = None
        pydevd_frame_evaluator = None
        found_unexpected = True
        if len(files) == 2:
            for f in files:
                if f.endswith('pydevd_cython.c'):
                    pydevd_cython = f

                elif f.endswith('pydevd_frame_evaluator.c'):
                    pydevd_frame_evaluator = f

            if pydevd_cython and pydevd_frame_evaluator:
                found_unexpected = False
                output = subprocess.check_output('git diff'.split())
                for line in output.decode('utf-8').splitlines():
                    if line.startswith('+') or line.startswith('-'):
                        if line.strip() not in expected_differences:
                            found_unexpected = True

        if files and found_unexpected:
            # If there are modifications, show a diff of the modifications and fail the script.
            # (we're mostly interested in modifications to the .c generated files by cython).
            print('Found modifications in git:\n%s ' % (output,))
            print('Files: %s' % (files,))
            print('----------- diff -------------')
            subprocess.call('git diff'.split())
            print('----------- end diff -------------')
            sys.exit(1)


if __name__ == '__main__':
    main()
